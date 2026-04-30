from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from tempfile import NamedTemporaryFile
from threading import RLock

from alpha_autopilot import ArtifactStore

from .common import clamp
from .schemas import (
    BenchmarkAuditExportResponse,
    BenchmarkIngestRequest,
    BenchmarkIngestResponse,
    BenchmarkParameterSet,
    BenchmarkQueryRequest,
    BenchmarkQueryResponse,
    BenchmarkRestoreResponse,
    BenchmarkVersionDiffResponse,
    BenchmarkVersionRecord,
)

MIN_CORRIDOR_SAMPLES = 5


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass
class _SnapshotDetail:
    version: str
    created_at: str
    trigger: str
    rows: list[dict[str, object]]
    total_rows: int
    active_rows: int
    rows_sha256: str
    integrity_status: str


class V7BenchmarkStore:
    def __init__(self, *, path: Path, version_root: Path | None = None) -> None:
        self.path = path
        self.version_root = version_root or (path.parent / f"{path.stem}_versions")
        self._lock = RLock()

    def ingest(self, payload: BenchmarkIngestRequest) -> BenchmarkIngestResponse:
        channel = _normalize_label(payload.channel)
        genre_track = _normalize_label(payload.genre_track)

        if not payload.sample_payload:
            return BenchmarkIngestResponse(
                accepted=False,
                version=self._state_version([]),
                recalibrated=False,
                message="empty_sample_payload",
            )

        with self._lock:
            rows = self._read_rows()
            if any(str(row.get("book_id", "")).strip() == payload.book_id for row in rows):
                return BenchmarkIngestResponse(
                    accepted=False,
                    version=self._state_version(rows),
                    recalibrated=False,
                    message="duplicate_book_id",
                )

            row = {
                "book_id": payload.book_id,
                "channel": channel,
                "genre_track": genre_track,
                "sample_payload": payload.sample_payload,
                "active": True,
                "created_at": _now_iso(),
                "nqm_mean": self._extract_mean(payload.sample_payload),
            }
            rows.append(row)
            version = self._persist_rows(rows, trigger="ingest")
            return BenchmarkIngestResponse(
                accepted=True,
                version=version,
                recalibrated=True,
                message="accepted",
            )

    def retract(self, book_id: str) -> bool:
        with self._lock:
            rows = self._read_rows()
            changed = False
            for row in rows:
                if str(row.get("book_id", "")).strip() == book_id and bool(row.get("active", True)):
                    row["active"] = False
                    row["retracted_at"] = _now_iso()
                    changed = True
            if changed:
                self._persist_rows(rows, trigger="retract")
            return changed

    def query(self, payload: BenchmarkQueryRequest) -> BenchmarkQueryResponse:
        channel = _normalize_label(payload.channel)
        genre_track = _normalize_label(payload.genre_track)
        with self._lock:
            rows = self._read_rows()

        active_rows = [row for row in rows if bool(row.get("active", True))]
        exact = [
            row
            for row in active_rows
            if str(row.get("channel", "unknown")) == channel
            and str(row.get("genre_track", "unknown")) == genre_track
        ]

        source_rows = exact
        warnings: list[str] = []

        if not source_rows:
            source_rows = [row for row in active_rows if str(row.get("channel", "unknown")) == channel]
            if source_rows:
                warnings.append("genre_fallback_to_channel")

        if not source_rows:
            fallback = BenchmarkParameterSet(channel=channel, genre_track=genre_track)
            return BenchmarkQueryResponse(
                benchmark=fallback,
                source_count=0,
                corridor_ready=False,
                warnings=["no_benchmark_samples"],
            )

        means = [float(row.get("nqm_mean", 0.62)) for row in source_rows]
        mean_value = sum(means) / len(means)
        variance = sum((item - mean_value) ** 2 for item in means) / max(1, len(means))
        std_value = max(0.01, variance**0.5)

        corridor_ready = len(source_rows) >= MIN_CORRIDOR_SAMPLES
        if not corridor_ready:
            warnings.append("insufficient_samples_for_corridor")

        benchmark = BenchmarkParameterSet(
            channel=channel,
            genre_track=genre_track,
            sample_count=len(source_rows),
            nqm_mean=clamp(mean_value),
            nqm_std=clamp(std_value, low=0.01, high=0.5),
            high_threshold=clamp(mean_value + 0.16),
            low_threshold=clamp(mean_value - 0.10),
            opening_gate_t8=0.60,
        )
        return BenchmarkQueryResponse(
            benchmark=benchmark,
            source_count=len(source_rows),
            corridor_ready=corridor_ready,
            warnings=warnings,
        )

    def list_versions(self, *, limit: int = 20) -> list[BenchmarkVersionRecord]:
        with self._lock:
            entries = self._read_version_entries()
        if limit <= 0:
            return []
        entries.sort(key=lambda item: item.created_at, reverse=True)
        return entries[:limit]

    def restore(self, version: str) -> BenchmarkRestoreResponse:
        version_id = str(version).strip()
        if not version_id:
            return self._failed_restore(
                requested_version="",
                active_rows=self._read_rows(),
                message="empty_version",
            )

        with self._lock:
            detail, reason = self._read_snapshot_detail(version_id)
            rows_now = self._read_rows()
            if detail is None:
                message = "version_not_found" if reason == "version_not_found" else "snapshot_invalid"
                return self._failed_restore(
                    requested_version=version_id,
                    active_rows=rows_now,
                    message=message,
                )
            if detail.integrity_status == "failed":
                return self._failed_restore(
                    requested_version=version_id,
                    active_rows=rows_now,
                    message="snapshot_integrity_failed",
                )

            backup_version = self._write_snapshot(rows_now, trigger=f"restore_backup:{version_id}")
            try:
                active_version = self._persist_rows(detail.rows, trigger=f"restore:{version_id}")
            except Exception:
                self._write_rows(rows_now)
                return self._failed_restore(
                    requested_version=version_id,
                    active_rows=rows_now,
                    message="restore_apply_failed",
                    backup_version=backup_version,
                )

            return BenchmarkRestoreResponse(
                restored=True,
                requested_version=version_id,
                active_version=active_version,
                total_rows=len(detail.rows),
                active_rows=self._active_count(detail.rows),
                integrity_verified=detail.integrity_status == "verified",
                backup_version=backup_version,
                message="restored" if detail.integrity_status == "verified" else "restored_unverified_snapshot",
            )

    def compare_versions(self, *, base_version: str, target_version: str) -> BenchmarkVersionDiffResponse:
        base_id = str(base_version).strip()
        target_id = str(target_version).strip()
        if not base_id or not target_id:
            return BenchmarkVersionDiffResponse(
                comparable=False,
                base_version=base_id,
                target_version=target_id,
                message="empty_version",
            )

        with self._lock:
            base_detail, base_reason = self._read_snapshot_detail(base_id)
            target_detail, target_reason = self._read_snapshot_detail(target_id)

        if base_detail is None:
            return BenchmarkVersionDiffResponse(
                comparable=False,
                base_version=base_id,
                target_version=target_id,
                message="base_version_not_found" if base_reason == "version_not_found" else "base_snapshot_invalid",
            )
        if target_detail is None:
            return BenchmarkVersionDiffResponse(
                comparable=False,
                base_version=base_id,
                target_version=target_id,
                message="target_version_not_found" if target_reason == "version_not_found" else "target_snapshot_invalid",
            )
        if base_detail.integrity_status == "failed":
            return BenchmarkVersionDiffResponse(
                comparable=False,
                base_version=base_id,
                target_version=target_id,
                message="base_snapshot_integrity_failed",
            )
        if target_detail.integrity_status == "failed":
            return BenchmarkVersionDiffResponse(
                comparable=False,
                base_version=base_id,
                target_version=target_id,
                message="target_snapshot_integrity_failed",
            )

        base_by_id = self._rows_by_book_id(base_detail.rows)
        target_by_id = self._rows_by_book_id(target_detail.rows)

        added: list[str] = []
        removed: list[str] = []
        activated: list[str] = []
        deactivated: list[str] = []
        mean_changed: list[str] = []

        all_ids = sorted(set(base_by_id) | set(target_by_id))
        for book_id in all_ids:
            base_row = base_by_id.get(book_id)
            target_row = target_by_id.get(book_id)
            if base_row is None:
                added.append(book_id)
                continue
            if target_row is None:
                removed.append(book_id)
                continue

            base_active = bool(base_row.get("active", True))
            target_active = bool(target_row.get("active", True))
            if not base_active and target_active:
                activated.append(book_id)
            if base_active and not target_active:
                deactivated.append(book_id)

            if abs(self._extract_row_mean(base_row) - self._extract_row_mean(target_row)) > 1e-9:
                mean_changed.append(book_id)

        return BenchmarkVersionDiffResponse(
            comparable=True,
            base_version=base_id,
            target_version=target_id,
            base_active_rows=base_detail.active_rows,
            target_active_rows=target_detail.active_rows,
            base_integrity_verified=base_detail.integrity_status == "verified",
            target_integrity_verified=target_detail.integrity_status == "verified",
            added_count=len(added),
            removed_count=len(removed),
            activated_count=len(activated),
            deactivated_count=len(deactivated),
            mean_changed_count=len(mean_changed),
            added_book_ids=added,
            removed_book_ids=removed,
            activated_book_ids=activated,
            deactivated_book_ids=deactivated,
            mean_changed_book_ids=mean_changed,
            message="comparable",
        )

    def export_audit(self, *, limit: int = 50) -> BenchmarkAuditExportResponse:
        versions = self.list_versions(limit=limit)
        verified = sum(1 for item in versions if item.integrity_status == "verified")
        unverified = sum(1 for item in versions if item.integrity_status == "unverified")
        failed = sum(1 for item in versions if item.integrity_status == "failed")
        return BenchmarkAuditExportResponse(
            generated_at=_now_iso(),
            latest_version=versions[0].version if versions else "",
            version_count=len(versions),
            integrity_verified_count=verified,
            integrity_unverified_count=unverified,
            integrity_failed_count=failed,
            versions=versions,
        )

    def _state_version(self, rows: list[dict[str, object]]) -> str:
        active_count = self._active_count(rows)
        return f"v7-benchmark-{len(rows):05d}-a{active_count:05d}"

    def _active_count(self, rows: list[dict[str, object]]) -> int:
        return sum(1 for row in rows if bool(row.get("active", True)))

    def _extract_mean(self, payload: dict[str, object]) -> float:
        if isinstance(payload.get("nqm_mean"), (int, float)):
            return clamp(float(payload["nqm_mean"]))
        if isinstance(payload.get("composite"), (int, float)):
            return clamp(float(payload["composite"]))
        return 0.62

    def _extract_row_mean(self, row: dict[str, object]) -> float:
        raw = row.get("nqm_mean", 0.62)
        try:
            return float(raw)
        except Exception:
            return 0.62

    def _rows_by_book_id(self, rows: list[dict[str, object]]) -> dict[str, dict[str, object]]:
        output: dict[str, dict[str, object]] = {}
        for row in rows:
            key = str(row.get("book_id", "")).strip()
            if not key:
                continue
            output[key] = row
        return output

    def _snapshot_file(self, version: str) -> Path:
        return self.version_root / f"{version}.json"

    def _persist_rows(self, rows: list[dict[str, object]], *, trigger: str) -> str:
        self._write_rows(rows)
        return self._write_snapshot(rows, trigger=trigger)

    def _write_snapshot(self, rows: list[dict[str, object]], *, trigger: str) -> str:
        self.version_root.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        version = f"{self._state_version(rows)}-{timestamp}"
        payload = {
            "version": version,
            "created_at": _now_iso(),
            "trigger": str(trigger or "unknown"),
            "total_rows": len(rows),
            "active_rows": self._active_count(rows),
            "rows_sha256": self._rows_digest(rows),
            "rows": rows,
        }
        self._atomic_write_json(self._snapshot_file(version), payload)
        return version

    def _rows_digest(self, rows: list[dict[str, object]]) -> str:
        canonical = json.dumps(rows, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def _read_snapshot_detail(self, version: str) -> tuple[_SnapshotDetail | None, str]:
        path = self._snapshot_file(version)
        if not path.exists():
            return None, "version_not_found"
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return None, "snapshot_parse_failed"
        return self._snapshot_detail_from_payload(payload, expected_version=version)

    def _snapshot_detail_from_payload(
        self,
        payload: object,
        *,
        expected_version: str | None = None,
    ) -> tuple[_SnapshotDetail | None, str]:
        if not isinstance(payload, dict):
            return None, "snapshot_payload_invalid"

        version = str(payload.get("version", "")).strip()
        created_at = str(payload.get("created_at", "")).strip()
        trigger = str(payload.get("trigger", "unknown")).strip() or "unknown"
        if not version or not created_at:
            return None, "snapshot_header_invalid"
        if expected_version and version != expected_version:
            return None, "snapshot_version_mismatch"

        if not isinstance(payload.get("rows"), list):
            return None, "snapshot_rows_invalid"
        rows = self._normalize_rows(payload.get("rows", []))
        rows_sha256 = str(payload.get("rows_sha256", "")).strip()
        integrity_status = "unverified"
        if rows_sha256:
            integrity_status = "verified" if self._rows_digest(rows) == rows_sha256 else "failed"

        total_rows = int(payload.get("total_rows", len(rows)) or len(rows))
        active_rows_raw = payload.get("active_rows", self._active_count(rows))
        try:
            active_rows = int(active_rows_raw)
        except Exception:
            active_rows = self._active_count(rows)

        detail = _SnapshotDetail(
            version=version,
            created_at=created_at,
            trigger=trigger,
            rows=rows,
            total_rows=total_rows,
            active_rows=max(0, active_rows),
            rows_sha256=rows_sha256,
            integrity_status=integrity_status,
        )
        return detail, "ok"

    def _read_version_entries(self) -> list[BenchmarkVersionRecord]:
        if not self.version_root.exists():
            return []

        output: list[BenchmarkVersionRecord] = []
        for file_path in sorted(self.version_root.glob("*.json"), key=lambda item: item.name):
            try:
                payload = json.loads(file_path.read_text(encoding="utf-8"))
            except Exception:
                continue
            detail, reason = self._snapshot_detail_from_payload(payload)
            if detail is None or reason != "ok":
                continue
            output.append(
                BenchmarkVersionRecord(
                    version=detail.version,
                    created_at=detail.created_at,
                    trigger=detail.trigger,
                    total_rows=detail.total_rows,
                    active_rows=detail.active_rows,
                    rows_sha256=detail.rows_sha256,
                    integrity_status=detail.integrity_status,
                )
            )
        return output

    def _failed_restore(
        self,
        *,
        requested_version: str,
        active_rows: list[dict[str, object]],
        message: str,
        backup_version: str = "",
    ) -> BenchmarkRestoreResponse:
        return BenchmarkRestoreResponse(
            restored=False,
            requested_version=requested_version,
            active_version=self._state_version(active_rows),
            total_rows=len(active_rows),
            active_rows=self._active_count(active_rows),
            integrity_verified=False,
            backup_version=backup_version,
            message=message,
        )

    def _normalize_rows(self, value: object) -> list[dict[str, object]]:
        if not isinstance(value, list):
            return []
        rows: list[dict[str, object]] = []
        for item in value:
            if isinstance(item, dict):
                rows.append(item)
        return rows

    def _read_rows(self) -> list[dict[str, object]]:
        if not self.path.exists():
            return []

        rows: list[dict[str, object]] = []
        for raw in self.path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except Exception:
                continue
            if isinstance(payload, dict):
                rows.append(payload)
        return rows

    def _write_rows(self, rows: list[dict[str, object]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile("w", delete=False, encoding="utf-8", dir=str(self.path.parent)) as tmp_file:
            for row in rows:
                tmp_file.write(json.dumps(row, ensure_ascii=False))
                tmp_file.write("\n")
            tmp_name = tmp_file.name
        Path(tmp_name).replace(self.path)

    def _atomic_write_json(self, path: Path, payload: dict[str, object]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile("w", delete=False, encoding="utf-8", dir=str(path.parent)) as tmp_file:
            tmp_file.write(json.dumps(payload, ensure_ascii=False))
            tmp_name = tmp_file.name
        Path(tmp_name).replace(path)


def create_default_v7_benchmark_store(root: Path | None = None) -> V7BenchmarkStore:
    artifact_store = ArtifactStore.default()
    base = root or (artifact_store.artifacts_dir / "history")
    return V7BenchmarkStore(path=base / "v7_benchmark_store.jsonl")


def _normalize_label(value: str) -> str:
    text = str(value or "unknown").strip().lower()
    return text or "unknown"
