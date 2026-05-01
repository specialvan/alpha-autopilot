from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from threading import RLock
from uuid import uuid4

from alpha_autopilot import ArtifactStore

from .common import clamp
from .schemas import (
    BenchmarkAuditExportResponse,
    BenchmarkIngestRequest,
    BenchmarkIngestResponse,
    BenchmarkMaintenanceAlertResponse,
    BenchmarkMaintenanceAlertEmitResponse,
    BenchmarkMaintenanceAlertEvent,
    BenchmarkMaintenanceAlertListResponse,
    BenchmarkMaintenanceAlertDigestResponse,
    BenchmarkMaintenanceAlertArchiveResponse,
    BenchmarkMaintenanceAlertArchiveFileRecord,
    BenchmarkMaintenanceAlertArchiveListResponse,
    BenchmarkMaintenanceAlertArchiveReadResponse,
    BenchmarkMaintenanceAlertArchiveCleanupResponse,
    BenchmarkMaintenanceAlertAutoArchiveResponse,
    BenchmarkMaintenanceAlertGovernancePolicy,
    BenchmarkMaintenanceAlertGovernanceReportResponse,
    BenchmarkMaintenanceAlertGovernanceRunListResponse,
    BenchmarkMaintenanceAlertGovernanceRunExportResponse,
    BenchmarkMaintenanceAlertGovernanceRunAutoPruneResponse,
    BenchmarkMaintenanceAlertGovernanceRunDigestResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationEvent,
    BenchmarkMaintenanceAlertGovernanceEscalationEmitResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationListResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationSummaryResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationExportResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationPruneResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationAutoPruneResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationDigestResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationAutoRemediateResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationRunRecord,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationListResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationSummaryResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationExportResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationPruneResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoPruneResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationDigestResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunRecord,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunListResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunSummaryResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunExportResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunPruneResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoPruneResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunDigestResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunRecord,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunListResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunSummaryResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunExportResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunPruneResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoPruneResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunDigestResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateRunRecord,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateRunListResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateRunSummaryResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateRunExportResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateRunPruneResponse,
    BenchmarkMaintenanceAlertGovernanceRunAutoRemediateResponse,
    BenchmarkMaintenanceAlertGovernanceRunPruneResponse,
    BenchmarkMaintenanceAlertGovernanceRunRecord,
    BenchmarkMaintenanceAlertGovernanceRunSummaryResponse,
    BenchmarkMaintenanceAlertGovernanceRunResponse,
    BenchmarkMaintenanceAlertExportResponse,
    BenchmarkMaintenanceAlertPruneResponse,
    BenchmarkMaintenanceAlertSummaryResponse,
    BenchmarkMaintenanceReportResponse,
    BenchmarkMaintenanceSlaPolicy,
    BenchmarkParameterSet,
    BenchmarkQueryRequest,
    BenchmarkQueryResponse,
    BenchmarkRestoreResponse,
    BenchmarkVersionDiffResponse,
    BenchmarkVersionAutoRemediateResponse,
    BenchmarkVersionHealthResponse,
    BenchmarkVersionPruneResponse,
    BenchmarkVersionRepairResponse,
    BenchmarkVersionRecord,
)

MIN_CORRIDOR_SAMPLES = 5


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _new_timestamped_id(prefix: str) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    # Windows clock resolution can repeat microsecond timestamps; add entropy.
    return f"{prefix}{timestamp}-{uuid4().hex[:8]}"


def _env_int(name: str, default: int, *, low: int = 0) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        return max(low, int(default))
    try:
        return max(low, int(raw))
    except Exception:
        return max(low, int(default))


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name, "").strip().lower()
    if not raw:
        return bool(default)
    if raw in {"1", "true", "yes", "y", "on"}:
        return True
    if raw in {"0", "false", "no", "n", "off"}:
        return False
    return bool(default)


def _parse_iso_utc(raw: str) -> datetime | None:
    text = str(raw or "").strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = f"{text[:-1]}+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except Exception:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _parse_cursor_offset(raw: str | None) -> int:
    text = str(raw or "").strip()
    if not text:
        return 0
    try:
        value = int(text)
    except Exception:
        return 0
    return max(0, value)


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

    def prune_versions(self, *, keep_last: int, dry_run: bool = True) -> BenchmarkVersionPruneResponse:
        keep_count = max(0, int(keep_last))
        with self._lock:
            entries = self._read_version_entries()
            entries.sort(key=lambda item: item.created_at, reverse=True)
            kept = entries[:keep_count]
            candidates = entries[keep_count:]

            pruned_versions: list[str] = []
            if not dry_run:
                for entry in candidates:
                    path = self._snapshot_file(entry.version)
                    if not path.exists():
                        continue
                    try:
                        path.unlink()
                        pruned_versions.append(entry.version)
                    except Exception:
                        continue

        return BenchmarkVersionPruneResponse(
            dry_run=bool(dry_run),
            keep_last=keep_count,
            version_count_before=len(entries),
            kept_count=len(kept),
            candidate_count=len(candidates),
            pruned_count=len(pruned_versions),
            kept_versions=[item.version for item in kept],
            pruned_versions=pruned_versions,
            message="dry_run" if dry_run else "pruned",
        )

    def scan_version_health(self) -> BenchmarkVersionHealthResponse:
        with self._lock:
            if not self.version_root.exists():
                return BenchmarkVersionHealthResponse(generated_at=_now_iso())

            total_files = 0
            valid_snapshot_count = 0
            verified_count = 0
            unverified_count = 0
            failed_integrity_count = 0
            malformed_file_count = 0
            failed_versions: list[str] = []
            malformed_files: list[str] = []

            for file_path in sorted(self.version_root.glob("*.json"), key=lambda item: item.name):
                total_files += 1
                try:
                    payload = json.loads(file_path.read_text(encoding="utf-8"))
                except Exception:
                    malformed_file_count += 1
                    malformed_files.append(file_path.name)
                    continue

                detail, reason = self._snapshot_detail_from_payload(payload)
                if detail is None or reason != "ok":
                    malformed_file_count += 1
                    malformed_files.append(file_path.name)
                    continue

                valid_snapshot_count += 1
                if detail.integrity_status == "verified":
                    verified_count += 1
                elif detail.integrity_status == "unverified":
                    unverified_count += 1
                elif detail.integrity_status == "failed":
                    failed_integrity_count += 1
                    failed_versions.append(detail.version)

        return BenchmarkVersionHealthResponse(
            generated_at=_now_iso(),
            total_files=total_files,
            valid_snapshot_count=valid_snapshot_count,
            verified_count=verified_count,
            unverified_count=unverified_count,
            failed_integrity_count=failed_integrity_count,
            malformed_file_count=malformed_file_count,
            failed_versions=failed_versions,
            malformed_files=malformed_files,
        )

    def repair_versions(self, *, dry_run: bool = True) -> BenchmarkVersionRepairResponse:
        with self._lock:
            if not self.version_root.exists():
                return BenchmarkVersionRepairResponse(
                    generated_at=_now_iso(),
                    dry_run=bool(dry_run),
                    message="empty_version_root",
                )

            failed_files: list[tuple[Path, str]] = []
            malformed_files: list[Path] = []
            total_files = 0

            for file_path in sorted(self.version_root.glob("*.json"), key=lambda item: item.name):
                total_files += 1
                try:
                    payload = json.loads(file_path.read_text(encoding="utf-8"))
                except Exception:
                    malformed_files.append(file_path)
                    continue

                detail, reason = self._snapshot_detail_from_payload(payload)
                if detail is None or reason != "ok":
                    malformed_files.append(file_path)
                    continue

                if detail.integrity_status == "failed":
                    failed_files.append((file_path, detail.version))

            if dry_run:
                return BenchmarkVersionRepairResponse(
                    generated_at=_now_iso(),
                    dry_run=True,
                    total_files=total_files,
                    candidate_failed_count=len(failed_files),
                    candidate_malformed_count=len(malformed_files),
                    moved_count=0,
                    moved_failed_count=0,
                    moved_malformed_count=0,
                    quarantine_dir="",
                    moved_files=[],
                    message="dry_run",
                )

            quarantine_dir = self.version_root / "_quarantine" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            quarantine_dir.mkdir(parents=True, exist_ok=True)

            moved_files: list[str] = []
            moved_failed_count = 0
            moved_malformed_count = 0

            for file_path, _version in failed_files:
                target = self._unique_target_path(quarantine_dir, file_path.name)
                try:
                    file_path.replace(target)
                    moved_failed_count += 1
                    moved_files.append(str(target.name))
                except Exception:
                    continue

            for file_path in malformed_files:
                target = self._unique_target_path(quarantine_dir, file_path.name)
                try:
                    file_path.replace(target)
                    moved_malformed_count += 1
                    moved_files.append(str(target.name))
                except Exception:
                    continue

            return BenchmarkVersionRepairResponse(
                generated_at=_now_iso(),
                dry_run=False,
                total_files=total_files,
                candidate_failed_count=len(failed_files),
                candidate_malformed_count=len(malformed_files),
                moved_count=moved_failed_count + moved_malformed_count,
                moved_failed_count=moved_failed_count,
                moved_malformed_count=moved_malformed_count,
                quarantine_dir=str(quarantine_dir),
                moved_files=moved_files,
                message="repaired",
            )

    def build_maintenance_report(self, *, limit: int = 50) -> BenchmarkMaintenanceReportResponse:
        audit = self.export_audit(limit=limit)
        health = self.scan_version_health()
        recommendations: list[str] = []
        severity: str = "ok"

        if health.failed_integrity_count > 0 or health.malformed_file_count > 0:
            severity = "critical"
            recommendations.append("Run benchmark version repair to quarantine failed/malformed snapshots.")
            recommendations.append("Review quarantined files and restore from verified snapshots when needed.")
        elif audit.integrity_unverified_count > 0:
            severity = "warn"
            recommendations.append("Backfill snapshot rows_sha256 for legacy unverified versions if possible.")

        if audit.version_count > 500:
            severity = "critical" if severity == "critical" else "warn"
            recommendations.append("Run benchmark version prune to control snapshot growth.")

        if not recommendations:
            recommendations.append("Benchmark version repository is healthy.")

        return BenchmarkMaintenanceReportResponse(
            generated_at=_now_iso(),
            severity=severity,
            recommendations=recommendations,
            audit=audit,
            health=health,
        )

    def auto_remediate_versions(self, *, dry_run: bool = True, keep_last: int = 50) -> BenchmarkVersionAutoRemediateResponse:
        health_before = self.scan_version_health()
        repair = self.repair_versions(dry_run=dry_run)
        prune = self.prune_versions(keep_last=keep_last, dry_run=dry_run)
        health_after = self.scan_version_health()

        if dry_run:
            message = "dry_run"
        elif repair.moved_count > 0 or prune.pruned_count > 0:
            message = "remediated"
        else:
            message = "no_action"

        return BenchmarkVersionAutoRemediateResponse(
            generated_at=_now_iso(),
            dry_run=bool(dry_run),
            keep_last=max(0, int(keep_last)),
            health_before=health_before,
            repair=repair,
            prune=prune,
            health_after=health_after,
            message=message,
        )

    def build_maintenance_alert(self, *, limit: int = 50) -> BenchmarkMaintenanceAlertResponse:
        report = self.build_maintenance_report(limit=limit)
        policy = self._load_maintenance_sla_policy()

        breaches: list[str] = []
        if report.health.failed_integrity_count > policy.max_failed_integrity:
            breaches.append(
                f"failed_integrity_exceeded:{report.health.failed_integrity_count}>{policy.max_failed_integrity}"
            )
        if report.health.malformed_file_count > policy.max_malformed_files:
            breaches.append(
                f"malformed_files_exceeded:{report.health.malformed_file_count}>{policy.max_malformed_files}"
            )
        if report.health.unverified_count > policy.max_unverified:
            breaches.append(f"unverified_exceeded:{report.health.unverified_count}>{policy.max_unverified}")
        if report.audit.version_count > policy.max_version_count_critical:
            breaches.append(
                f"version_count_critical_exceeded:{report.audit.version_count}>{policy.max_version_count_critical}"
            )
        elif report.audit.version_count > policy.max_version_count_warn:
            breaches.append(f"version_count_warn_exceeded:{report.audit.version_count}>{policy.max_version_count_warn}")

        level = "ok"
        if any(
            item.startswith("failed_integrity_exceeded:")
            or item.startswith("malformed_files_exceeded:")
            or item.startswith("version_count_critical_exceeded:")
            for item in breaches
        ):
            level = "critical"
        elif breaches:
            level = "warn"

        should_page = bool(policy.page_on_critical and level == "critical")
        should_ticket = bool(should_page or (policy.ticket_on_warn and level == "warn"))

        return BenchmarkMaintenanceAlertResponse(
            generated_at=_now_iso(),
            level=level,
            should_page=should_page,
            should_ticket=should_ticket,
            breaches=breaches,
            policy=policy,
            report=report,
        )

    def emit_maintenance_alert(self, *, limit: int = 50) -> BenchmarkMaintenanceAlertEmitResponse:
        alert = self.build_maintenance_alert(limit=limit)
        event = BenchmarkMaintenanceAlertEvent(
            event_id=_new_timestamped_id("bm-alert-"),
            generated_at=_now_iso(),
            level=alert.level,
            should_page=alert.should_page,
            should_ticket=alert.should_ticket,
            breaches=list(alert.breaches),
            report_severity=alert.report.severity,
        )

        with self._lock:
            path = self._alerts_path()
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(event.model_dump(mode="json"), ensure_ascii=False))
                handle.write("\n")

        return BenchmarkMaintenanceAlertEmitResponse(alert=alert, event=event)

    def list_maintenance_alerts(
        self,
        *,
        limit: int = 100,
        cursor: str = "",
    ) -> BenchmarkMaintenanceAlertListResponse:
        query_limit = max(0, int(limit))
        offset = _parse_cursor_offset(cursor)
        with self._lock:
            path = self._alerts_path()
            if not path.exists():
                return BenchmarkMaintenanceAlertListResponse(
                    limit=query_limit,
                    cursor=str(offset),
                    alerts=[],
                    message="no_alerts",
                )
            rows, malformed_line_count = self._read_alert_events(path=path)
        rows.sort(key=lambda item: item.generated_at, reverse=True)
        total = len(rows)
        start = min(offset, total)
        end = min(total, start + query_limit) if query_limit > 0 else total
        window = rows[start:end]
        has_more = end < total
        next_cursor = str(end) if has_more else ""
        return BenchmarkMaintenanceAlertListResponse(
            limit=query_limit,
            cursor=str(start),
            next_cursor=next_cursor,
            has_more=has_more,
            total_valid_events=total,
            malformed_line_count=malformed_line_count,
            alerts=window,
            message="ok",
        )

    def prune_maintenance_alerts(
        self,
        *,
        keep_last: int,
        dry_run: bool = True,
    ) -> BenchmarkMaintenanceAlertPruneResponse:
        keep_count = max(0, int(keep_last))
        with self._lock:
            path = self._alerts_path()
            if not path.exists():
                return BenchmarkMaintenanceAlertPruneResponse(
                    dry_run=bool(dry_run),
                    keep_last=keep_count,
                    message="no_alerts",
                )

            rows, malformed_candidate_count = self._read_alert_events(path=path)
            rows.sort(key=lambda item: item.generated_at, reverse=True)
            kept = rows[:keep_count]
            candidates = rows[keep_count:]

            pruned_event_ids: list[str] = []
            malformed_dropped_count = 0
            if not dry_run:
                serialized = [
                    json.dumps(item.model_dump(mode="json"), ensure_ascii=False)
                    for item in kept
                ]
                temp_path = path.with_suffix(f"{path.suffix}.tmp")
                payload = "\n".join(serialized)
                if payload:
                    payload += "\n"
                temp_path.write_text(payload, encoding="utf-8")
                temp_path.replace(path)
                pruned_event_ids = [item.event_id for item in candidates]
                malformed_dropped_count = malformed_candidate_count

        return BenchmarkMaintenanceAlertPruneResponse(
            dry_run=bool(dry_run),
            keep_last=keep_count,
            total_alerts_before=len(rows),
            kept_count=len(kept),
            candidate_count=len(candidates),
            pruned_count=len(pruned_event_ids),
            malformed_candidate_count=malformed_candidate_count,
            malformed_dropped_count=malformed_dropped_count,
            kept_event_ids=[item.event_id for item in kept],
            pruned_event_ids=pruned_event_ids,
            message="dry_run" if dry_run else "pruned",
        )

    def summarize_maintenance_alerts(self, *, limit: int = 200) -> BenchmarkMaintenanceAlertSummaryResponse:
        query_limit = max(0, int(limit))
        with self._lock:
            path = self._alerts_path()
            if not path.exists():
                return BenchmarkMaintenanceAlertSummaryResponse(
                    generated_at=_now_iso(),
                    limit=query_limit,
                    message="no_alerts",
                )
            rows, malformed_line_count = self._read_alert_events(path=path)

        rows.sort(key=lambda item: item.generated_at, reverse=True)
        window = rows[:query_limit] if query_limit > 0 else rows

        ok_count = sum(1 for item in window if item.level == "ok")
        warn_count = sum(1 for item in window if item.level == "warn")
        critical_count = sum(1 for item in window if item.level == "critical")
        page_event_count = sum(1 for item in window if item.should_page)
        ticket_event_count = sum(1 for item in window if item.should_ticket)
        breach_event_count = sum(1 for item in window if item.breaches)

        return BenchmarkMaintenanceAlertSummaryResponse(
            generated_at=_now_iso(),
            limit=query_limit,
            total_valid_events=len(rows),
            window_event_count=len(window),
            malformed_line_count=malformed_line_count,
            ok_count=ok_count,
            warn_count=warn_count,
            critical_count=critical_count,
            page_event_count=page_event_count,
            ticket_event_count=ticket_event_count,
            breach_event_count=breach_event_count,
            latest_event=rows[0] if rows else None,
            message="ok",
        )

    def archive_maintenance_alerts(
        self,
        *,
        keep_last: int,
        shard_size: int = 1000,
        dry_run: bool = True,
    ) -> BenchmarkMaintenanceAlertArchiveResponse:
        keep_count = max(0, int(keep_last))
        shard_count = max(1, int(shard_size))
        with self._lock:
            path = self._alerts_path()
            if not path.exists():
                return BenchmarkMaintenanceAlertArchiveResponse(
                    generated_at=_now_iso(),
                    dry_run=bool(dry_run),
                    keep_last=keep_count,
                    shard_size=shard_count,
                    message="no_alerts",
                )

            rows, malformed_candidate_count = self._read_alert_events(path=path)
            rows.sort(key=lambda item: item.generated_at, reverse=True)
            kept = rows[:keep_count]
            candidates = rows[keep_count:]

            archive_dir = self._alerts_archive_dir()
            archive_files: list[str] = []
            archived_count = 0
            malformed_dropped_count = 0

            if not dry_run:
                self._write_alert_events(path=path, events=kept)
                if candidates:
                    archive_dir.mkdir(parents=True, exist_ok=True)
                    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
                    oldest_first = list(reversed(candidates))
                    for index in range(0, len(oldest_first), shard_count):
                        chunk = oldest_first[index : index + shard_count]
                        shard_name = f"alerts-{timestamp}-{(index // shard_count) + 1:04d}.jsonl"
                        shard_path = self._unique_target_path(archive_dir, shard_name)
                        self._write_alert_events(path=shard_path, events=chunk)
                        archive_files.append(shard_path.name)
                    archived_count = len(candidates)
                malformed_dropped_count = malformed_candidate_count

        return BenchmarkMaintenanceAlertArchiveResponse(
            generated_at=_now_iso(),
            dry_run=bool(dry_run),
            keep_last=keep_count,
            shard_size=shard_count,
            total_valid_events_before=len(rows),
            kept_count=len(kept),
            candidate_count=len(candidates),
            archived_count=archived_count,
            archive_shard_count=len(archive_files),
            malformed_candidate_count=malformed_candidate_count,
            malformed_dropped_count=malformed_dropped_count,
            archive_dir=str(archive_dir),
            archive_files=archive_files,
            message="dry_run" if dry_run else "archived",
        )

    def list_maintenance_alert_archive_files(self, *, limit: int = 200) -> BenchmarkMaintenanceAlertArchiveListResponse:
        query_limit = max(0, int(limit))
        with self._lock:
            archive_dir = self._alerts_archive_dir()
            if not archive_dir.exists():
                return BenchmarkMaintenanceAlertArchiveListResponse(
                    generated_at=_now_iso(),
                    total_files=0,
                    files=[],
                    message="no_archive",
                )

            all_files = sorted(archive_dir.glob("*.jsonl"), key=lambda item: item.name, reverse=True)
            selected = all_files[:query_limit] if query_limit > 0 else all_files
            records: list[BenchmarkMaintenanceAlertArchiveFileRecord] = []
            for item in selected:
                rows, malformed_line_count = self._read_alert_events(path=item)
                try:
                    modified_at = datetime.fromtimestamp(item.stat().st_mtime, tz=timezone.utc).isoformat().replace(
                        "+00:00", "Z"
                    )
                    size_bytes = int(item.stat().st_size)
                except Exception:
                    modified_at = ""
                    size_bytes = 0
                records.append(
                    BenchmarkMaintenanceAlertArchiveFileRecord(
                        file_name=item.name,
                        size_bytes=max(0, size_bytes),
                        modified_at=modified_at,
                        valid_event_count=len(rows),
                        malformed_line_count=malformed_line_count,
                    )
                )

        return BenchmarkMaintenanceAlertArchiveListResponse(
            generated_at=_now_iso(),
            total_files=len(all_files),
            files=records,
            message="ok",
        )

    def read_maintenance_alert_archive_file(
        self,
        *,
        file_name: str,
        limit: int = 100,
        cursor: str = "",
    ) -> BenchmarkMaintenanceAlertArchiveReadResponse:
        query_limit = max(0, int(limit))
        offset = _parse_cursor_offset(cursor)
        requested_name = str(file_name or "").strip()
        normalized_name = Path(requested_name).name
        if not normalized_name or normalized_name != requested_name:
            return BenchmarkMaintenanceAlertArchiveReadResponse(
                file_name=normalized_name,
                limit=query_limit,
                cursor=str(offset),
                message="invalid_file_name",
            )

        with self._lock:
            path = self._alerts_archive_dir() / normalized_name
            if not path.exists():
                return BenchmarkMaintenanceAlertArchiveReadResponse(
                    file_name=normalized_name,
                    limit=query_limit,
                    cursor=str(offset),
                    message="file_not_found",
                )
            rows, malformed_line_count = self._read_alert_events(path=path)

        rows.sort(key=lambda item: item.generated_at, reverse=True)
        total = len(rows)
        start = min(offset, total)
        end = min(total, start + query_limit) if query_limit > 0 else total
        window = rows[start:end]
        has_more = end < total
        next_cursor = str(end) if has_more else ""

        return BenchmarkMaintenanceAlertArchiveReadResponse(
            file_name=normalized_name,
            limit=query_limit,
            cursor=str(start),
            next_cursor=next_cursor,
            has_more=has_more,
            total_valid_events=total,
            malformed_line_count=malformed_line_count,
            alerts=window,
            message="ok",
        )

    def auto_archive_maintenance_alerts(self, *, dry_run: bool = True) -> BenchmarkMaintenanceAlertAutoArchiveResponse:
        policy = self._load_alert_governance_policy()
        trigger_count = policy.archive_trigger_count
        keep_last = policy.archive_keep_last
        shard_size = policy.archive_shard_size

        with self._lock:
            path = self._alerts_path()
            if path.exists():
                rows, malformed_line_count = self._read_alert_events(path=path)
            else:
                rows = []
                malformed_line_count = 0

        total_valid_events = len(rows)
        should_archive = total_valid_events > trigger_count or malformed_line_count > 0
        if not should_archive:
            return BenchmarkMaintenanceAlertAutoArchiveResponse(
                generated_at=_now_iso(),
                dry_run=bool(dry_run),
                trigger_count=trigger_count,
                keep_last=keep_last,
                shard_size=shard_size,
                total_valid_events=total_valid_events,
                malformed_line_count=malformed_line_count,
                should_archive=False,
                archive=None,
                message="below_threshold",
            )

        archive = self.archive_maintenance_alerts(
            keep_last=keep_last,
            shard_size=shard_size,
            dry_run=dry_run,
        )
        return BenchmarkMaintenanceAlertAutoArchiveResponse(
            generated_at=_now_iso(),
            dry_run=bool(dry_run),
            trigger_count=trigger_count,
            keep_last=keep_last,
            shard_size=shard_size,
            total_valid_events=total_valid_events,
            malformed_line_count=malformed_line_count,
            should_archive=True,
            archive=archive,
            message="archived" if not dry_run else "dry_run",
        )

    def cleanup_maintenance_alert_archives(self, *, dry_run: bool = True) -> BenchmarkMaintenanceAlertArchiveCleanupResponse:
        policy = self._load_alert_governance_policy()
        ttl_days = policy.archive_ttl_days
        max_shard_files = policy.archive_max_shard_files
        ttl_seconds = float(ttl_days) * 86400.0
        now_ts = datetime.now(timezone.utc).timestamp()

        with self._lock:
            archive_dir = self._alerts_archive_dir()
            if not archive_dir.exists():
                return BenchmarkMaintenanceAlertArchiveCleanupResponse(
                    generated_at=_now_iso(),
                    dry_run=bool(dry_run),
                    ttl_days=ttl_days,
                    max_shard_files=max_shard_files,
                    archive_dir=str(archive_dir),
                    message="no_archive",
                )

            files = sorted(archive_dir.glob("*.jsonl"), key=lambda item: item.name)
            if not files:
                return BenchmarkMaintenanceAlertArchiveCleanupResponse(
                    generated_at=_now_iso(),
                    dry_run=bool(dry_run),
                    ttl_days=ttl_days,
                    max_shard_files=max_shard_files,
                    archive_dir=str(archive_dir),
                    message="no_archive",
                )

            metas: list[tuple[Path, float]] = []
            for path in files:
                try:
                    mtime = float(path.stat().st_mtime)
                except Exception:
                    mtime = 0.0
                metas.append((path, mtime))

            sorted_by_newest = sorted(metas, key=lambda item: (item[1], item[0].name), reverse=True)
            ttl_candidates = {
                path
                for path, mtime in metas
                if ttl_seconds <= 0.0 or (now_ts - mtime) > ttl_seconds
            }
            max_candidates = {
                path for path, _mtime in sorted_by_newest[max_shard_files:]
            }
            candidates = sorted(ttl_candidates | max_candidates, key=lambda item: item.name)

            removed_files: list[str] = []
            if not dry_run:
                for path in candidates:
                    try:
                        path.unlink()
                        removed_files.append(path.name)
                    except Exception:
                        continue

        total_files = len(files)
        candidate_count = len(candidates)
        removed_count = len(removed_files)
        kept_count = total_files - (removed_count if not dry_run else candidate_count)
        return BenchmarkMaintenanceAlertArchiveCleanupResponse(
            generated_at=_now_iso(),
            dry_run=bool(dry_run),
            ttl_days=ttl_days,
            max_shard_files=max_shard_files,
            total_files=total_files,
            kept_count=max(0, kept_count),
            candidate_count=candidate_count,
            removed_count=removed_count,
            ttl_candidate_count=len(ttl_candidates),
            max_shard_candidate_count=len(max_candidates),
            archive_dir=str(self._alerts_archive_dir()),
            candidate_files=[path.name for path in candidates],
            removed_files=removed_files,
            message="dry_run" if dry_run else "cleaned",
        )

    def build_maintenance_alert_governance_report(
        self,
        *,
        alert_limit: int = 200,
        archive_limit: int = 200,
    ) -> BenchmarkMaintenanceAlertGovernanceReportResponse:
        limit_alert = max(0, int(alert_limit))
        limit_archive = max(0, int(archive_limit))
        policy = self._load_alert_governance_policy()
        active_summary = self.summarize_maintenance_alerts(limit=limit_alert)
        archive_index = self.list_maintenance_alert_archive_files(limit=limit_archive)
        projected_auto_archive = self.auto_archive_maintenance_alerts(dry_run=True)
        projected_archive_cleanup = self.cleanup_maintenance_alert_archives(dry_run=True)
        return BenchmarkMaintenanceAlertGovernanceReportResponse(
            generated_at=_now_iso(),
            alert_limit=limit_alert,
            archive_limit=limit_archive,
            policy=policy,
            active_summary=active_summary,
            archive_index=archive_index,
            projected_auto_archive=projected_auto_archive,
            projected_archive_cleanup=projected_archive_cleanup,
            message="ok",
        )

    def run_maintenance_alert_governance(
        self,
        *,
        dry_run: bool = True,
        alert_limit: int = 200,
        archive_limit: int = 200,
        idempotency_key: str = "",
        retry_run_id: str = "",
    ) -> BenchmarkMaintenanceAlertGovernanceRunResponse:
        limit_alert = max(0, int(alert_limit))
        limit_archive = max(0, int(archive_limit))
        normalized_idempotency_key = str(idempotency_key or "").strip()
        normalized_retry_run_id = str(retry_run_id or "").strip()
        request_fingerprint = self._governance_run_fingerprint(
            dry_run=dry_run,
            alert_limit=limit_alert,
            archive_limit=limit_archive,
            retry_run_id=normalized_retry_run_id,
        )

        with self._lock:
            run_log_path = self._governance_runs_path()
            if run_log_path.exists():
                records, _malformed_count = self._read_governance_run_records(path=run_log_path)
            else:
                records = []

        if normalized_idempotency_key:
            previous = next(
                (item for item in reversed(records) if item.idempotency_key == normalized_idempotency_key),
                None,
            )
            if previous is not None:
                if previous.request_fingerprint and previous.request_fingerprint != request_fingerprint:
                    raise ValueError("idempotency_key_reused_with_different_request")
                if previous.status == "succeeded" and previous.response_payload:
                    reused = BenchmarkMaintenanceAlertGovernanceRunResponse.model_validate(previous.response_payload)
                    reused.idempotency_reused = True
                    reused.message = "idempotent_replay"
                    return reused

        policy = self._load_alert_governance_policy()
        attempt = 1
        if normalized_retry_run_id:
            retry_target = next((item for item in reversed(records) if item.run_id == normalized_retry_run_id), None)
            if retry_target is None:
                raise ValueError("retry_target_not_found")
            if retry_target.status != "failed":
                raise ValueError("retry_target_not_failed")
            if retry_target.attempt >= policy.governance_runs_max_retry_attempts:
                raise ValueError("retry_attempt_limit_exceeded")
            attempt = retry_target.attempt + 1

        run_id = self._next_governance_run_id()
        started_at = _now_iso()

        try:
            active_summary_before = self.summarize_maintenance_alerts(limit=limit_alert)
            archive_index_before = self.list_maintenance_alert_archive_files(limit=limit_archive)
            auto_archive = self.auto_archive_maintenance_alerts(dry_run=dry_run)
            archive_cleanup = self.cleanup_maintenance_alert_archives(dry_run=dry_run)
            active_summary_after = self.summarize_maintenance_alerts(limit=limit_alert)
            archive_index_after = self.list_maintenance_alert_archive_files(limit=limit_archive)

            performed_steps = [
                "auto_archive:scheduled" if auto_archive.should_archive else "auto_archive:skipped",
                "archive_cleanup:scheduled" if archive_cleanup.candidate_count > 0 else "archive_cleanup:noop",
            ]
            response = BenchmarkMaintenanceAlertGovernanceRunResponse(
                run_id=run_id,
                generated_at=started_at,
                dry_run=bool(dry_run),
                alert_limit=limit_alert,
                archive_limit=limit_archive,
                idempotency_key=normalized_idempotency_key,
                request_fingerprint=request_fingerprint,
                retry_run_id=normalized_retry_run_id,
                attempt=attempt,
                idempotency_reused=False,
                policy=policy,
                performed_steps=performed_steps,
                active_summary_before=active_summary_before,
                active_summary_after=active_summary_after,
                archive_index_before=archive_index_before,
                archive_index_after=archive_index_after,
                auto_archive=auto_archive,
                archive_cleanup=archive_cleanup,
                message="dry_run" if dry_run else "governed",
            )
            record = BenchmarkMaintenanceAlertGovernanceRunRecord(
                run_id=run_id,
                generated_at=started_at,
                completed_at=_now_iso(),
                status="succeeded",
                dry_run=bool(dry_run),
                alert_limit=limit_alert,
                archive_limit=limit_archive,
                idempotency_key=normalized_idempotency_key,
                request_fingerprint=request_fingerprint,
                retry_run_id=normalized_retry_run_id,
                attempt=attempt,
                performed_steps=performed_steps,
                auto_archive_should_archive=auto_archive.should_archive,
                archive_cleanup_candidate_count=archive_cleanup.candidate_count,
                result_message=response.message,
                response_payload=response.model_dump(mode="json"),
            )
            with self._lock:
                self._append_governance_run_record(path=self._governance_runs_path(), record=record)
            return response
        except Exception as exc:
            failed_record = BenchmarkMaintenanceAlertGovernanceRunRecord(
                run_id=run_id,
                generated_at=started_at,
                completed_at=_now_iso(),
                status="failed",
                dry_run=bool(dry_run),
                alert_limit=limit_alert,
                archive_limit=limit_archive,
                idempotency_key=normalized_idempotency_key,
                request_fingerprint=request_fingerprint,
                retry_run_id=normalized_retry_run_id,
                attempt=attempt,
                error_type=type(exc).__name__,
                error_message=str(exc),
                result_message="failed",
            )
            with self._lock:
                self._append_governance_run_record(path=self._governance_runs_path(), record=failed_record)
            raise

    def list_maintenance_alert_governance_runs(
        self,
        *,
        limit: int = 100,
        cursor: str = "",
    ) -> BenchmarkMaintenanceAlertGovernanceRunListResponse:
        query_limit = max(0, int(limit))
        offset = _parse_cursor_offset(cursor)
        with self._lock:
            path = self._governance_runs_path()
            if not path.exists():
                return BenchmarkMaintenanceAlertGovernanceRunListResponse(
                    limit=query_limit,
                    cursor=str(offset),
                    records=[],
                    message="no_runs",
                )
            records, malformed_line_count = self._read_governance_run_records(path=path)

        ordered_records = self._order_governance_run_records(records)
        total = len(ordered_records)
        start = min(offset, total)
        end = min(total, start + query_limit) if query_limit > 0 else total
        window = ordered_records[start:end]
        has_more = end < total
        next_cursor = str(end) if has_more else ""

        return BenchmarkMaintenanceAlertGovernanceRunListResponse(
            limit=query_limit,
            cursor=str(start),
            next_cursor=next_cursor,
            has_more=has_more,
            total_records=total,
            malformed_line_count=malformed_line_count,
            records=window,
            message="ok",
        )

    def summarize_maintenance_alert_governance_runs(
        self,
        *,
        limit: int = 200,
    ) -> BenchmarkMaintenanceAlertGovernanceRunSummaryResponse:
        query_limit = max(0, int(limit))
        with self._lock:
            path = self._governance_runs_path()
            if not path.exists():
                return BenchmarkMaintenanceAlertGovernanceRunSummaryResponse(
                    generated_at=_now_iso(),
                    limit=query_limit,
                    message="no_runs",
                )
            records, malformed_line_count = self._read_governance_run_records(path=path)

        ordered_records = self._order_governance_run_records(records)
        window = ordered_records[:query_limit] if query_limit > 0 else ordered_records
        latest_failed_run = next((item for item in ordered_records if item.status == "failed"), None)
        consecutive_failed_runs = 0
        for item in ordered_records:
            if item.status == "failed":
                consecutive_failed_runs += 1
            else:
                break

        return BenchmarkMaintenanceAlertGovernanceRunSummaryResponse(
            generated_at=_now_iso(),
            limit=query_limit,
            total_records=len(ordered_records),
            window_record_count=len(window),
            malformed_line_count=malformed_line_count,
            succeeded_count=sum(1 for item in window if item.status == "succeeded"),
            failed_count=sum(1 for item in window if item.status == "failed"),
            consecutive_failed_runs=consecutive_failed_runs,
            latest_run=ordered_records[0] if ordered_records else None,
            latest_failed_run=latest_failed_run,
            message="ok",
        )

    def export_maintenance_alert_governance_runs(
        self,
        *,
        limit: int = 200,
        cursor: str = "",
    ) -> BenchmarkMaintenanceAlertGovernanceRunExportResponse:
        query_limit = max(0, int(limit))
        summary = self.summarize_maintenance_alert_governance_runs(limit=query_limit)
        page = self.list_maintenance_alert_governance_runs(limit=query_limit, cursor=cursor)
        return BenchmarkMaintenanceAlertGovernanceRunExportResponse(
            generated_at=_now_iso(),
            limit=query_limit,
            cursor=page.cursor,
            next_cursor=page.next_cursor,
            has_more=page.has_more,
            total_records=page.total_records,
            malformed_line_count=page.malformed_line_count,
            summary=summary,
            records=page.records,
            message="ok",
        )

    def auto_prune_maintenance_alert_governance_runs(
        self,
        *,
        dry_run: bool = True,
    ) -> BenchmarkMaintenanceAlertGovernanceRunAutoPruneResponse:
        policy = self._load_alert_governance_policy()
        trigger_count = policy.governance_runs_prune_trigger_count
        keep_last = policy.governance_runs_prune_keep_last

        with self._lock:
            path = self._governance_runs_path()
            if path.exists():
                rows, malformed_line_count = self._read_governance_run_records(path=path)
            else:
                rows = []
                malformed_line_count = 0

        total_records = len(rows)
        should_prune = total_records > trigger_count or malformed_line_count > 0
        if not should_prune:
            return BenchmarkMaintenanceAlertGovernanceRunAutoPruneResponse(
                generated_at=_now_iso(),
                dry_run=bool(dry_run),
                trigger_count=trigger_count,
                keep_last=keep_last,
                total_records=total_records,
                malformed_line_count=malformed_line_count,
                should_prune=False,
                prune=None,
                message="below_threshold",
            )

        prune = self.prune_maintenance_alert_governance_runs(keep_last=keep_last, dry_run=dry_run)
        return BenchmarkMaintenanceAlertGovernanceRunAutoPruneResponse(
            generated_at=_now_iso(),
            dry_run=bool(dry_run),
            trigger_count=trigger_count,
            keep_last=keep_last,
            total_records=total_records,
            malformed_line_count=malformed_line_count,
            should_prune=True,
            prune=prune,
            message="pruned" if not dry_run else "dry_run",
        )

    def build_maintenance_alert_governance_runs_digest(
        self,
        *,
        limit: int = 200,
    ) -> BenchmarkMaintenanceAlertGovernanceRunDigestResponse:
        summary = self.summarize_maintenance_alert_governance_runs(limit=limit)
        stale_threshold_seconds = _env_int("AA_V7_BENCH_GOVERNANCE_RUNS_STALE_SECONDS", 900, low=0)
        policy = self._load_alert_governance_policy()
        retry_max_attempts = max(1, int(policy.governance_runs_max_retry_attempts))
        escalation_failure_streak_limit = max(1, int(policy.governance_runs_escalation_failure_streak))

        latest_run_age_seconds = -1.0
        is_stale = True
        latest_failed_attempt = summary.latest_failed_run.attempt if summary.latest_failed_run is not None else 0
        if summary.latest_run is not None and summary.latest_run.status == "failed":
            latest_failed_attempt = max(latest_failed_attempt, summary.latest_run.attempt)
        retry_exhausted = latest_failed_attempt >= retry_max_attempts and latest_failed_attempt > 0
        failure_streak_exhausted = summary.consecutive_failed_runs >= escalation_failure_streak_limit

        if summary.latest_run is not None:
            parsed_latest = _parse_iso_utc(summary.latest_run.generated_at)
            if parsed_latest is not None:
                latest_run_age_seconds = max(0.0, (datetime.now(timezone.utc) - parsed_latest).total_seconds())
                is_stale = latest_run_age_seconds > stale_threshold_seconds
            else:
                is_stale = True

        if summary.latest_run is None:
            recommended_action = "execute_governance_run"
            message = "no_runs"
        elif summary.latest_run.status == "failed":
            if retry_exhausted:
                recommended_action = "escalate_failed_run"
                message = "retry_exhausted"
            elif failure_streak_exhausted:
                recommended_action = "escalate_failed_run"
                message = "consecutive_failure_streak_exhausted"
            else:
                recommended_action = "retry_latest_failed_run"
                message = "failed_latest_run"
        elif summary.malformed_line_count > 0:
            recommended_action = "auto_prune_runs"
            message = "malformed_detected"
        elif summary.total_records > policy.governance_runs_prune_trigger_count:
            recommended_action = "auto_prune_runs"
            message = "above_prune_threshold"
        elif is_stale:
            recommended_action = "execute_governance_run"
            message = "stale"
        else:
            recommended_action = "observe"
            message = "ok"

        return BenchmarkMaintenanceAlertGovernanceRunDigestResponse(
            generated_at=_now_iso(),
            stale_threshold_seconds=stale_threshold_seconds,
            latest_run_age_seconds=latest_run_age_seconds,
            retry_max_attempts=retry_max_attempts,
            latest_failed_attempt=latest_failed_attempt,
            retry_exhausted=retry_exhausted,
            escalation_failure_streak_limit=escalation_failure_streak_limit,
            failure_streak_exhausted=failure_streak_exhausted,
            is_stale=is_stale,
            recommended_action=recommended_action,
            summary=summary,
            message=message,
        )

    def emit_maintenance_alert_governance_escalation(
        self,
        *,
        limit: int = 200,
        source: str = "manual_emit",
        ignore_cooldown: bool = False,
    ) -> BenchmarkMaintenanceAlertGovernanceEscalationEmitResponse:
        query_limit = max(0, int(limit))
        digest = self.build_maintenance_alert_governance_runs_digest(limit=query_limit)
        source_tag = "auto_remediate" if str(source or "").strip() == "auto_remediate" else "manual_emit"
        policy = self._load_alert_governance_policy()
        cooldown_seconds = max(0, int(policy.governance_escalations_emit_cooldown_seconds))

        if digest.recommended_action != "escalate_failed_run":
            return BenchmarkMaintenanceAlertGovernanceEscalationEmitResponse(
                generated_at=_now_iso(),
                limit=query_limit,
                emitted=False,
                suppressed=False,
                suppression_reason="",
                suppressed_by_event_id="",
                cooldown_seconds=cooldown_seconds,
                digest=digest,
                event=None,
                message="no_escalation_needed",
            )

        escalation_reason = self._resolve_governance_escalation_reason(digest=digest)
        latest_run_id = digest.summary.latest_run.run_id if digest.summary.latest_run is not None else ""
        latest_failed_run_id = (
            digest.summary.latest_failed_run.run_id if digest.summary.latest_failed_run is not None else ""
        )
        event = BenchmarkMaintenanceAlertGovernanceEscalationEvent(
            event_id=_new_timestamped_id("bm-governance-escalation-"),
            generated_at=_now_iso(),
            source=source_tag,
            recommended_action=digest.recommended_action,
            escalation_reason=escalation_reason,
            digest_message=digest.message,
            latest_run_id=latest_run_id,
            latest_failed_run_id=latest_failed_run_id,
            consecutive_failed_runs=digest.summary.consecutive_failed_runs,
            latest_failed_attempt=digest.latest_failed_attempt,
            retry_max_attempts=digest.retry_max_attempts,
            escalation_failure_streak_limit=digest.escalation_failure_streak_limit,
            retry_exhausted=digest.retry_exhausted,
            failure_streak_exhausted=digest.failure_streak_exhausted,
        )

        if not bool(ignore_cooldown) and cooldown_seconds > 0:
            with self._lock:
                path = self._governance_escalations_path()
                if path.exists():
                    rows, _ = self._read_governance_escalation_events(path=path)
                    ordered_rows = self._order_governance_escalation_events(rows)
                else:
                    ordered_rows = []
            if ordered_rows:
                latest = ordered_rows[0]
                latest_time = _parse_iso_utc(latest.generated_at)
                latest_age_seconds = -1.0
                if latest_time is not None:
                    latest_age_seconds = max(0.0, (datetime.now(timezone.utc) - latest_time).total_seconds())
                same_signature = (
                    latest.source == source_tag
                    and latest.escalation_reason == escalation_reason
                    and latest.latest_failed_run_id == latest_failed_run_id
                    and latest.retry_exhausted == digest.retry_exhausted
                    and latest.failure_streak_exhausted == digest.failure_streak_exhausted
                )
                if same_signature and 0.0 <= latest_age_seconds <= float(cooldown_seconds):
                    return BenchmarkMaintenanceAlertGovernanceEscalationEmitResponse(
                        generated_at=_now_iso(),
                        limit=query_limit,
                        emitted=False,
                        suppressed=True,
                        suppression_reason="cooldown_active",
                        suppressed_by_event_id=latest.event_id,
                        cooldown_seconds=cooldown_seconds,
                        digest=digest,
                        event=latest,
                        message="escalation_suppressed_cooldown",
                    )

        with self._lock:
            path = self._governance_escalations_path()
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(event.model_dump(mode="json"), ensure_ascii=False))
                handle.write("\n")
        return BenchmarkMaintenanceAlertGovernanceEscalationEmitResponse(
            generated_at=_now_iso(),
            limit=query_limit,
            emitted=True,
            suppressed=False,
            suppression_reason="",
            suppressed_by_event_id="",
            cooldown_seconds=cooldown_seconds,
            digest=digest,
            event=event,
            message="escalation_emitted",
        )

    def list_maintenance_alert_governance_escalations(
        self,
        *,
        limit: int = 100,
        cursor: str = "",
    ) -> BenchmarkMaintenanceAlertGovernanceEscalationListResponse:
        query_limit = max(0, int(limit))
        offset = _parse_cursor_offset(cursor)
        with self._lock:
            path = self._governance_escalations_path()
            if not path.exists():
                return BenchmarkMaintenanceAlertGovernanceEscalationListResponse(
                    limit=query_limit,
                    cursor=str(offset),
                    events=[],
                    message="no_escalations",
                )
            rows, malformed_line_count = self._read_governance_escalation_events(path=path)
        ordered_rows = self._order_governance_escalation_events(rows)
        total = len(ordered_rows)
        start = min(offset, total)
        end = min(total, start + query_limit) if query_limit > 0 else total
        window = ordered_rows[start:end]
        has_more = end < total
        next_cursor = str(end) if has_more else ""
        return BenchmarkMaintenanceAlertGovernanceEscalationListResponse(
            limit=query_limit,
            cursor=str(start),
            next_cursor=next_cursor,
            has_more=has_more,
            total_events=total,
            malformed_line_count=malformed_line_count,
            events=window,
            message="ok",
        )

    def summarize_maintenance_alert_governance_escalations(
        self,
        *,
        limit: int = 200,
    ) -> BenchmarkMaintenanceAlertGovernanceEscalationSummaryResponse:
        query_limit = max(0, int(limit))
        with self._lock:
            path = self._governance_escalations_path()
            if not path.exists():
                return BenchmarkMaintenanceAlertGovernanceEscalationSummaryResponse(
                    generated_at=_now_iso(),
                    limit=query_limit,
                    message="no_escalations",
                )
            rows, malformed_line_count = self._read_governance_escalation_events(path=path)

        ordered_rows = self._order_governance_escalation_events(rows)
        window = ordered_rows[:query_limit] if query_limit > 0 else ordered_rows
        return BenchmarkMaintenanceAlertGovernanceEscalationSummaryResponse(
            generated_at=_now_iso(),
            limit=query_limit,
            total_events=len(ordered_rows),
            window_event_count=len(window),
            malformed_line_count=malformed_line_count,
            manual_emit_count=sum(1 for item in window if item.source == "manual_emit"),
            auto_remediate_count=sum(1 for item in window if item.source == "auto_remediate"),
            retry_exhausted_count=sum(1 for item in window if item.retry_exhausted),
            failure_streak_exhausted_count=sum(1 for item in window if item.failure_streak_exhausted),
            latest_event=ordered_rows[0] if ordered_rows else None,
            message="ok",
        )

    def export_maintenance_alert_governance_escalations(
        self,
        *,
        limit: int = 200,
        cursor: str = "",
    ) -> BenchmarkMaintenanceAlertGovernanceEscalationExportResponse:
        query_limit = max(0, int(limit))
        summary = self.summarize_maintenance_alert_governance_escalations(limit=query_limit)
        page = self.list_maintenance_alert_governance_escalations(limit=query_limit, cursor=cursor)
        return BenchmarkMaintenanceAlertGovernanceEscalationExportResponse(
            generated_at=_now_iso(),
            limit=query_limit,
            cursor=page.cursor,
            next_cursor=page.next_cursor,
            has_more=page.has_more,
            total_events=page.total_events,
            malformed_line_count=page.malformed_line_count,
            summary=summary,
            events=page.events,
            message="ok",
        )

    def prune_maintenance_alert_governance_escalations(
        self,
        *,
        keep_last: int,
        dry_run: bool = True,
    ) -> BenchmarkMaintenanceAlertGovernanceEscalationPruneResponse:
        keep_count = max(0, int(keep_last))
        with self._lock:
            path = self._governance_escalations_path()
            if not path.exists():
                return BenchmarkMaintenanceAlertGovernanceEscalationPruneResponse(
                    generated_at=_now_iso(),
                    dry_run=bool(dry_run),
                    keep_last=keep_count,
                    message="no_escalations",
                )

            rows, malformed_candidate_count = self._read_governance_escalation_events(path=path)
            ordered_rows = self._order_governance_escalation_events(rows)
            kept = ordered_rows[:keep_count]
            candidates = ordered_rows[keep_count:]

            pruned_event_ids: list[str] = []
            malformed_dropped_count = 0
            if not dry_run:
                self._write_governance_escalation_events(path=path, events=kept)
                pruned_event_ids = [item.event_id for item in candidates]
                malformed_dropped_count = malformed_candidate_count

        return BenchmarkMaintenanceAlertGovernanceEscalationPruneResponse(
            generated_at=_now_iso(),
            dry_run=bool(dry_run),
            keep_last=keep_count,
            total_events_before=len(rows),
            kept_count=len(kept),
            candidate_count=len(candidates),
            pruned_count=len(pruned_event_ids),
            malformed_candidate_count=malformed_candidate_count,
            malformed_dropped_count=malformed_dropped_count,
            kept_event_ids=[item.event_id for item in kept],
            pruned_event_ids=pruned_event_ids,
            message="dry_run" if dry_run else "pruned",
        )

    def auto_prune_maintenance_alert_governance_escalations(
        self,
        *,
        dry_run: bool = True,
    ) -> BenchmarkMaintenanceAlertGovernanceEscalationAutoPruneResponse:
        policy = self._load_alert_governance_policy()
        trigger_count = policy.governance_escalations_prune_trigger_count
        keep_last = policy.governance_escalations_prune_keep_last

        with self._lock:
            path = self._governance_escalations_path()
            if path.exists():
                rows, malformed_line_count = self._read_governance_escalation_events(path=path)
            else:
                rows = []
                malformed_line_count = 0

        total_events = len(rows)
        should_prune = total_events > trigger_count or malformed_line_count > 0
        if not should_prune:
            return BenchmarkMaintenanceAlertGovernanceEscalationAutoPruneResponse(
                generated_at=_now_iso(),
                dry_run=bool(dry_run),
                trigger_count=trigger_count,
                keep_last=keep_last,
                total_events=total_events,
                malformed_line_count=malformed_line_count,
                should_prune=False,
                prune=None,
                message="below_threshold",
            )

        prune = self.prune_maintenance_alert_governance_escalations(keep_last=keep_last, dry_run=dry_run)
        return BenchmarkMaintenanceAlertGovernanceEscalationAutoPruneResponse(
            generated_at=_now_iso(),
            dry_run=bool(dry_run),
            trigger_count=trigger_count,
            keep_last=keep_last,
            total_events=total_events,
            malformed_line_count=malformed_line_count,
            should_prune=True,
            prune=prune,
            message="pruned" if not dry_run else "dry_run",
        )

    def build_maintenance_alert_governance_escalations_digest(
        self,
        *,
        limit: int = 200,
    ) -> BenchmarkMaintenanceAlertGovernanceEscalationDigestResponse:
        query_limit = max(0, int(limit))
        summary = self.summarize_maintenance_alert_governance_escalations(limit=query_limit)
        run_digest = self.build_maintenance_alert_governance_runs_digest(limit=query_limit)
        policy = self._load_alert_governance_policy()
        stale_threshold_seconds = _env_int("AA_V7_BENCH_GOVERNANCE_ESCALATIONS_STALE_SECONDS", 900, low=0)

        latest_event_age_seconds = -1.0
        is_stale = True
        if summary.latest_event is not None:
            parsed_latest = _parse_iso_utc(summary.latest_event.generated_at)
            if parsed_latest is not None:
                latest_event_age_seconds = max(0.0, (datetime.now(timezone.utc) - parsed_latest).total_seconds())
                is_stale = latest_event_age_seconds > stale_threshold_seconds
            else:
                is_stale = True

        if summary.malformed_line_count > 0:
            recommended_action = "auto_prune_escalations"
            message = "malformed_detected"
        elif summary.total_events > policy.governance_escalations_prune_trigger_count:
            recommended_action = "auto_prune_escalations"
            message = "above_prune_threshold"
        elif run_digest.recommended_action == "escalate_failed_run" and (summary.latest_event is None or is_stale):
            recommended_action = "emit_escalation"
            message = "escalation_needed"
        elif summary.latest_event is None:
            recommended_action = "observe"
            message = "no_escalations"
        elif is_stale:
            recommended_action = "observe"
            message = "stale"
        else:
            recommended_action = "observe"
            message = "ok"

        return BenchmarkMaintenanceAlertGovernanceEscalationDigestResponse(
            generated_at=_now_iso(),
            stale_threshold_seconds=stale_threshold_seconds,
            latest_event_age_seconds=latest_event_age_seconds,
            is_stale=is_stale,
            recommended_action=recommended_action,
            summary=summary,
            run_digest=run_digest,
            message=message,
        )

    def auto_remediate_maintenance_alert_governance_escalations(
        self,
        *,
        dry_run: bool = True,
        limit: int = 200,
    ) -> BenchmarkMaintenanceAlertGovernanceEscalationAutoRemediateResponse:
        query_limit = max(0, int(limit))
        digest_before = self.build_maintenance_alert_governance_escalations_digest(limit=query_limit)
        action = str(digest_before.recommended_action or "observe")

        emitted = False
        pruned = False
        emitted_event: BenchmarkMaintenanceAlertGovernanceEscalationEvent | None = None
        auto_prune: BenchmarkMaintenanceAlertGovernanceEscalationAutoPruneResponse | None = None

        if action == "emit_escalation":
            if not dry_run:
                emit_result = self.emit_maintenance_alert_governance_escalation(limit=query_limit, source="auto_remediate")
                emitted = bool(emit_result.emitted and emit_result.event is not None)
                emitted_event = emit_result.event
        elif action == "auto_prune_escalations":
            auto_prune = self.auto_prune_maintenance_alert_governance_escalations(dry_run=dry_run)
            if not dry_run and auto_prune.prune is not None:
                pruned = bool(
                    auto_prune.prune.pruned_count > 0
                    or auto_prune.prune.malformed_dropped_count > 0
                )

        executed = emitted or pruned
        digest_after = self.build_maintenance_alert_governance_escalations_digest(limit=query_limit)
        if dry_run:
            message = "dry_run"
        elif executed:
            message = "remediated"
        else:
            message = "no_action"

        response = BenchmarkMaintenanceAlertGovernanceEscalationAutoRemediateResponse(
            generated_at=_now_iso(),
            dry_run=bool(dry_run),
            limit=query_limit,
            action=action,
            executed=executed,
            emitted=emitted,
            pruned=pruned,
            emitted_event=emitted_event,
            auto_prune=auto_prune,
            digest_before=digest_before,
            digest_after=digest_after,
            message=message,
        )
        run_record = BenchmarkMaintenanceAlertGovernanceEscalationRemediationRunRecord(
            run_id=_new_timestamped_id("bm-governance-escalation-remediate-"),
            generated_at=response.generated_at,
            dry_run=bool(dry_run),
            limit=query_limit,
            action=action,
            executed=executed,
            emitted=emitted,
            pruned=pruned,
            emitted_event_id=emitted_event.event_id if emitted_event is not None else "",
            auto_prune_pruned_count=(
                auto_prune.prune.pruned_count
                if auto_prune is not None and auto_prune.prune is not None
                else 0
            ),
            auto_prune_malformed_dropped_count=(
                auto_prune.prune.malformed_dropped_count
                if auto_prune is not None and auto_prune.prune is not None
                else 0
            ),
            digest_before_message=digest_before.message,
            digest_after_message=digest_after.message,
            message=message,
        )
        with self._lock:
            self._append_governance_escalation_remediation_run_record(
                path=self._governance_escalation_remediations_path(),
                record=run_record,
            )
        return response

    def list_maintenance_alert_governance_escalation_remediations(
        self,
        *,
        limit: int = 100,
        cursor: str = "",
    ) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationListResponse:
        query_limit = max(0, int(limit))
        offset = _parse_cursor_offset(cursor)
        with self._lock:
            path = self._governance_escalation_remediations_path()
            if not path.exists():
                return BenchmarkMaintenanceAlertGovernanceEscalationRemediationListResponse(
                    limit=query_limit,
                    cursor=str(offset),
                    records=[],
                    message="no_records",
                )
            rows, malformed_line_count = self._read_governance_escalation_remediation_run_records(path=path)

        ordered_rows = self._order_governance_escalation_remediation_run_records(rows)
        total = len(ordered_rows)
        start = min(offset, total)
        end = min(total, start + query_limit) if query_limit > 0 else total
        window = ordered_rows[start:end]
        has_more = end < total
        next_cursor = str(end) if has_more else ""
        return BenchmarkMaintenanceAlertGovernanceEscalationRemediationListResponse(
            limit=query_limit,
            cursor=str(start),
            next_cursor=next_cursor,
            has_more=has_more,
            total_records=total,
            malformed_line_count=malformed_line_count,
            records=window,
            message="ok",
        )

    def summarize_maintenance_alert_governance_escalation_remediations(
        self,
        *,
        limit: int = 200,
    ) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationSummaryResponse:
        query_limit = max(0, int(limit))
        with self._lock:
            path = self._governance_escalation_remediations_path()
            if not path.exists():
                return BenchmarkMaintenanceAlertGovernanceEscalationRemediationSummaryResponse(
                    generated_at=_now_iso(),
                    limit=query_limit,
                    message="no_records",
                )
            rows, malformed_line_count = self._read_governance_escalation_remediation_run_records(path=path)

        ordered_rows = self._order_governance_escalation_remediation_run_records(rows)
        window = ordered_rows[:query_limit] if query_limit > 0 else ordered_rows
        return BenchmarkMaintenanceAlertGovernanceEscalationRemediationSummaryResponse(
            generated_at=_now_iso(),
            limit=query_limit,
            total_records=len(ordered_rows),
            window_record_count=len(window),
            malformed_line_count=malformed_line_count,
            dry_run_count=sum(1 for item in window if item.dry_run),
            apply_count=sum(1 for item in window if not item.dry_run),
            executed_count=sum(1 for item in window if item.executed),
            emitted_count=sum(1 for item in window if item.emitted),
            pruned_count=sum(1 for item in window if item.pruned),
            latest_record=ordered_rows[0] if ordered_rows else None,
            message="ok",
        )

    def export_maintenance_alert_governance_escalation_remediations(
        self,
        *,
        limit: int = 200,
        cursor: str = "",
    ) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationExportResponse:
        query_limit = max(0, int(limit))
        summary = self.summarize_maintenance_alert_governance_escalation_remediations(limit=query_limit)
        page = self.list_maintenance_alert_governance_escalation_remediations(limit=query_limit, cursor=cursor)
        return BenchmarkMaintenanceAlertGovernanceEscalationRemediationExportResponse(
            generated_at=_now_iso(),
            limit=query_limit,
            cursor=page.cursor,
            next_cursor=page.next_cursor,
            has_more=page.has_more,
            total_records=page.total_records,
            malformed_line_count=page.malformed_line_count,
            summary=summary,
            records=page.records,
            message="ok",
        )

    def prune_maintenance_alert_governance_escalation_remediations(
        self,
        *,
        keep_last: int,
        dry_run: bool = True,
    ) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationPruneResponse:
        keep_count = max(0, int(keep_last))
        with self._lock:
            path = self._governance_escalation_remediations_path()
            if not path.exists():
                return BenchmarkMaintenanceAlertGovernanceEscalationRemediationPruneResponse(
                    generated_at=_now_iso(),
                    dry_run=bool(dry_run),
                    keep_last=keep_count,
                    message="no_records",
                )

            rows, malformed_candidate_count = self._read_governance_escalation_remediation_run_records(path=path)
            ordered_rows = self._order_governance_escalation_remediation_run_records(rows)
            kept = ordered_rows[:keep_count]
            candidates = ordered_rows[keep_count:]

            pruned_run_ids: list[str] = []
            malformed_dropped_count = 0
            if not dry_run:
                self._write_governance_escalation_remediation_run_records(path=path, records=kept)
                pruned_run_ids = [item.run_id for item in candidates]
                malformed_dropped_count = malformed_candidate_count

        return BenchmarkMaintenanceAlertGovernanceEscalationRemediationPruneResponse(
            generated_at=_now_iso(),
            dry_run=bool(dry_run),
            keep_last=keep_count,
            total_records_before=len(rows),
            kept_count=len(kept),
            candidate_count=len(candidates),
            pruned_count=len(pruned_run_ids),
            malformed_candidate_count=malformed_candidate_count,
            malformed_dropped_count=malformed_dropped_count,
            kept_run_ids=[item.run_id for item in kept],
            pruned_run_ids=pruned_run_ids,
            message="dry_run" if dry_run else "pruned",
        )

    def auto_prune_maintenance_alert_governance_escalation_remediations(
        self,
        *,
        dry_run: bool = True,
    ) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoPruneResponse:
        policy = self._load_alert_governance_policy()
        trigger_count = policy.governance_escalation_remediations_prune_trigger_count
        keep_last = policy.governance_escalation_remediations_prune_keep_last

        with self._lock:
            path = self._governance_escalation_remediations_path()
            if path.exists():
                rows, malformed_line_count = self._read_governance_escalation_remediation_run_records(path=path)
            else:
                rows = []
                malformed_line_count = 0

        total_records = len(rows)
        should_prune = total_records > trigger_count or malformed_line_count > 0
        if not should_prune:
            return BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoPruneResponse(
                generated_at=_now_iso(),
                dry_run=bool(dry_run),
                trigger_count=trigger_count,
                keep_last=keep_last,
                total_records=total_records,
                malformed_line_count=malformed_line_count,
                should_prune=False,
                prune=None,
                message="below_threshold",
            )

        prune = self.prune_maintenance_alert_governance_escalation_remediations(keep_last=keep_last, dry_run=dry_run)
        return BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoPruneResponse(
            generated_at=_now_iso(),
            dry_run=bool(dry_run),
            trigger_count=trigger_count,
            keep_last=keep_last,
            total_records=total_records,
            malformed_line_count=malformed_line_count,
            should_prune=True,
            prune=prune,
            message="pruned" if not dry_run else "dry_run",
        )

    def build_maintenance_alert_governance_escalation_remediations_digest(
        self,
        *,
        limit: int = 200,
    ) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationDigestResponse:
        query_limit = max(0, int(limit))
        summary = self.summarize_maintenance_alert_governance_escalation_remediations(limit=query_limit)
        policy = self._load_alert_governance_policy()
        stale_threshold_seconds = max(0, int(policy.governance_escalation_remediations_stale_seconds))

        latest_record_age_seconds = -1.0
        is_stale = True
        if summary.latest_record is not None:
            parsed_latest = _parse_iso_utc(summary.latest_record.generated_at)
            if parsed_latest is not None:
                latest_record_age_seconds = max(0.0, (datetime.now(timezone.utc) - parsed_latest).total_seconds())
                is_stale = latest_record_age_seconds > float(stale_threshold_seconds)
            else:
                is_stale = True

        if summary.latest_record is None:
            recommended_action = "run_auto_remediate_escalations"
            message = "no_records"
        elif summary.malformed_line_count > 0:
            recommended_action = "auto_prune_remediations"
            message = "malformed_detected"
        elif summary.total_records > policy.governance_escalation_remediations_prune_trigger_count:
            recommended_action = "auto_prune_remediations"
            message = "above_prune_threshold"
        elif is_stale:
            recommended_action = "run_auto_remediate_escalations"
            message = "stale"
        else:
            recommended_action = "observe"
            message = "ok"

        return BenchmarkMaintenanceAlertGovernanceEscalationRemediationDigestResponse(
            generated_at=_now_iso(),
            stale_threshold_seconds=stale_threshold_seconds,
            latest_record_age_seconds=latest_record_age_seconds,
            is_stale=is_stale,
            recommended_action=recommended_action,
            summary=summary,
            message=message,
        )

    def auto_remediate_maintenance_alert_governance_escalation_remediations(
        self,
        *,
        dry_run: bool = True,
        limit: int = 200,
    ) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateResponse:
        query_limit = max(0, int(limit))
        digest_before = self.build_maintenance_alert_governance_escalation_remediations_digest(limit=query_limit)
        action = str(digest_before.recommended_action or "observe")

        remediated_escalations = False
        pruned_remediation_history = False
        escalation_auto_remediate: BenchmarkMaintenanceAlertGovernanceEscalationAutoRemediateResponse | None = None
        remediation_auto_prune: BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoPruneResponse | None = None

        if action == "run_auto_remediate_escalations":
            escalation_auto_remediate = self.auto_remediate_maintenance_alert_governance_escalations(
                dry_run=dry_run,
                limit=query_limit,
            )
            if not dry_run:
                remediated_escalations = bool(escalation_auto_remediate.executed)
        elif action == "auto_prune_remediations":
            remediation_auto_prune = self.auto_prune_maintenance_alert_governance_escalation_remediations(dry_run=dry_run)
            if not dry_run and remediation_auto_prune.prune is not None:
                pruned_remediation_history = bool(
                    remediation_auto_prune.prune.pruned_count > 0
                    or remediation_auto_prune.prune.malformed_dropped_count > 0
                )

        executed = remediated_escalations or pruned_remediation_history
        digest_after = self.build_maintenance_alert_governance_escalation_remediations_digest(limit=query_limit)
        if dry_run:
            message = "dry_run"
        elif executed:
            message = "remediated"
        else:
            message = "no_action"

        response = BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateResponse(
            generated_at=_now_iso(),
            dry_run=bool(dry_run),
            limit=query_limit,
            action=action,
            executed=executed,
            remediated_escalations=remediated_escalations,
            pruned_remediation_history=pruned_remediation_history,
            escalation_auto_remediate=escalation_auto_remediate,
            remediation_auto_prune=remediation_auto_prune,
            digest_before=digest_before,
            digest_after=digest_after,
            message=message,
        )
        run_record = BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunRecord(
            run_id=_new_timestamped_id("bm-governance-escalation-remediation-auto-remediate-"),
            generated_at=response.generated_at,
            dry_run=bool(dry_run),
            limit=query_limit,
            action=action,
            executed=executed,
            remediated_escalations=remediated_escalations,
            pruned_remediation_history=pruned_remediation_history,
            digest_before_message=digest_before.message,
            digest_after_message=digest_after.message,
            message=message,
        )
        with self._lock:
            self._append_governance_escalation_remediation_auto_remediate_run_record(
                path=self._governance_escalation_remediation_auto_remediate_runs_path(),
                record=run_record,
            )
        return response

    def list_maintenance_alert_governance_escalation_remediation_auto_remediate_runs(
        self,
        *,
        limit: int = 100,
        cursor: str = "",
    ) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunListResponse:
        query_limit = max(0, int(limit))
        offset = _parse_cursor_offset(cursor)
        with self._lock:
            path = self._governance_escalation_remediation_auto_remediate_runs_path()
            if not path.exists():
                return BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunListResponse(
                    limit=query_limit,
                    cursor=str(offset),
                    records=[],
                    message="no_records",
                )
            rows, malformed_line_count = self._read_governance_escalation_remediation_auto_remediate_run_records(path=path)

        ordered_rows = self._order_governance_escalation_remediation_auto_remediate_run_records(rows)
        total = len(ordered_rows)
        start = min(offset, total)
        end = min(total, start + query_limit) if query_limit > 0 else total
        window = ordered_rows[start:end]
        has_more = end < total
        next_cursor = str(end) if has_more else ""
        return BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunListResponse(
            limit=query_limit,
            cursor=str(start),
            next_cursor=next_cursor,
            has_more=has_more,
            total_records=total,
            malformed_line_count=malformed_line_count,
            records=window,
            message="ok",
        )

    def summarize_maintenance_alert_governance_escalation_remediation_auto_remediate_runs(
        self,
        *,
        limit: int = 200,
    ) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunSummaryResponse:
        query_limit = max(0, int(limit))
        with self._lock:
            path = self._governance_escalation_remediation_auto_remediate_runs_path()
            if not path.exists():
                return BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunSummaryResponse(
                    generated_at=_now_iso(),
                    limit=query_limit,
                    message="no_records",
                )
            rows, malformed_line_count = self._read_governance_escalation_remediation_auto_remediate_run_records(path=path)

        ordered_rows = self._order_governance_escalation_remediation_auto_remediate_run_records(rows)
        window = ordered_rows[:query_limit] if query_limit > 0 else ordered_rows
        return BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunSummaryResponse(
            generated_at=_now_iso(),
            limit=query_limit,
            total_records=len(ordered_rows),
            window_record_count=len(window),
            malformed_line_count=malformed_line_count,
            dry_run_count=sum(1 for item in window if item.dry_run),
            apply_count=sum(1 for item in window if not item.dry_run),
            executed_count=sum(1 for item in window if item.executed),
            remediated_escalations_count=sum(1 for item in window if item.remediated_escalations),
            pruned_remediation_history_count=sum(1 for item in window if item.pruned_remediation_history),
            latest_record=ordered_rows[0] if ordered_rows else None,
            message="ok",
        )

    def export_maintenance_alert_governance_escalation_remediation_auto_remediate_runs(
        self,
        *,
        limit: int = 200,
        cursor: str = "",
    ) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunExportResponse:
        query_limit = max(0, int(limit))
        summary = self.summarize_maintenance_alert_governance_escalation_remediation_auto_remediate_runs(limit=query_limit)
        page = self.list_maintenance_alert_governance_escalation_remediation_auto_remediate_runs(
            limit=query_limit,
            cursor=cursor,
        )
        return BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunExportResponse(
            generated_at=_now_iso(),
            limit=query_limit,
            cursor=page.cursor,
            next_cursor=page.next_cursor,
            has_more=page.has_more,
            total_records=page.total_records,
            malformed_line_count=page.malformed_line_count,
            summary=summary,
            records=page.records,
            message="ok",
        )

    def prune_maintenance_alert_governance_escalation_remediation_auto_remediate_runs(
        self,
        *,
        keep_last: int,
        dry_run: bool = True,
    ) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunPruneResponse:
        keep_count = max(0, int(keep_last))
        with self._lock:
            path = self._governance_escalation_remediation_auto_remediate_runs_path()
            if not path.exists():
                return BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunPruneResponse(
                    generated_at=_now_iso(),
                    dry_run=bool(dry_run),
                    keep_last=keep_count,
                    message="no_records",
                )

            rows, malformed_candidate_count = self._read_governance_escalation_remediation_auto_remediate_run_records(path=path)
            ordered_rows = self._order_governance_escalation_remediation_auto_remediate_run_records(rows)
            kept = ordered_rows[:keep_count]
            candidates = ordered_rows[keep_count:]

            pruned_run_ids: list[str] = []
            malformed_dropped_count = 0
            if not dry_run:
                self._write_governance_escalation_remediation_auto_remediate_run_records(path=path, records=kept)
                pruned_run_ids = [item.run_id for item in candidates]
                malformed_dropped_count = malformed_candidate_count

        return BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunPruneResponse(
            generated_at=_now_iso(),
            dry_run=bool(dry_run),
            keep_last=keep_count,
            total_records_before=len(rows),
            kept_count=len(kept),
            candidate_count=len(candidates),
            pruned_count=len(pruned_run_ids),
            malformed_candidate_count=malformed_candidate_count,
            malformed_dropped_count=malformed_dropped_count,
            kept_run_ids=[item.run_id for item in kept],
            pruned_run_ids=pruned_run_ids,
            message="dry_run" if dry_run else "pruned",
        )

    def auto_prune_maintenance_alert_governance_escalation_remediation_auto_remediate_runs(
        self,
        *,
        dry_run: bool = True,
    ) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoPruneResponse:
        policy = self._load_alert_governance_policy()
        trigger_count = policy.governance_escalation_remediation_auto_remediate_runs_prune_trigger_count
        keep_last = policy.governance_escalation_remediation_auto_remediate_runs_prune_keep_last

        with self._lock:
            path = self._governance_escalation_remediation_auto_remediate_runs_path()
            if path.exists():
                rows, malformed_line_count = self._read_governance_escalation_remediation_auto_remediate_run_records(path=path)
            else:
                rows = []
                malformed_line_count = 0

        total_records = len(rows)
        should_prune = total_records > trigger_count or malformed_line_count > 0
        if not should_prune:
            return BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoPruneResponse(
                generated_at=_now_iso(),
                dry_run=bool(dry_run),
                trigger_count=trigger_count,
                keep_last=keep_last,
                total_records=total_records,
                malformed_line_count=malformed_line_count,
                should_prune=False,
                prune=None,
                message="below_threshold",
            )

        prune = self.prune_maintenance_alert_governance_escalation_remediation_auto_remediate_runs(
            keep_last=keep_last,
            dry_run=dry_run,
        )
        return BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoPruneResponse(
            generated_at=_now_iso(),
            dry_run=bool(dry_run),
            trigger_count=trigger_count,
            keep_last=keep_last,
            total_records=total_records,
            malformed_line_count=malformed_line_count,
            should_prune=True,
            prune=prune,
            message="pruned" if not dry_run else "dry_run",
        )

    def build_maintenance_alert_governance_escalation_remediation_auto_remediate_runs_digest(
        self,
        *,
        limit: int = 200,
    ) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunDigestResponse:
        query_limit = max(0, int(limit))
        summary = self.summarize_maintenance_alert_governance_escalation_remediation_auto_remediate_runs(limit=query_limit)
        policy = self._load_alert_governance_policy()
        stale_threshold_seconds = max(0, int(policy.governance_escalation_remediation_auto_remediate_runs_stale_seconds))

        latest_record_age_seconds = -1.0
        is_stale = True
        if summary.latest_record is not None:
            parsed_latest = _parse_iso_utc(summary.latest_record.generated_at)
            if parsed_latest is not None:
                latest_record_age_seconds = max(0.0, (datetime.now(timezone.utc) - parsed_latest).total_seconds())
                is_stale = latest_record_age_seconds > float(stale_threshold_seconds)
            else:
                is_stale = True

        if summary.latest_record is None:
            recommended_action = "run_auto_remediation_orchestrator"
            message = "no_records"
        elif summary.malformed_line_count > 0:
            recommended_action = "auto_prune_runs"
            message = "malformed_detected"
        elif summary.total_records > policy.governance_escalation_remediation_auto_remediate_runs_prune_trigger_count:
            recommended_action = "auto_prune_runs"
            message = "above_prune_threshold"
        elif is_stale:
            recommended_action = "run_auto_remediation_orchestrator"
            message = "stale"
        else:
            recommended_action = "observe"
            message = "ok"

        return BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunDigestResponse(
            generated_at=_now_iso(),
            stale_threshold_seconds=stale_threshold_seconds,
            latest_record_age_seconds=latest_record_age_seconds,
            is_stale=is_stale,
            recommended_action=recommended_action,
            summary=summary,
            message=message,
        )

    def auto_remediate_maintenance_alert_governance_escalation_remediation_auto_remediate_runs(
        self,
        *,
        dry_run: bool = True,
        limit: int = 200,
    ) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateResponse:
        query_limit = max(0, int(limit))
        digest_before = self.build_maintenance_alert_governance_escalation_remediation_auto_remediate_runs_digest(
            limit=query_limit
        )
        action = str(digest_before.recommended_action or "observe")

        remediated_orchestrator = False
        pruned_run_history = False
        orchestrator_auto_remediate: BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateResponse | None = None
        run_history_auto_prune: (
            BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoPruneResponse | None
        ) = None

        if action == "run_auto_remediation_orchestrator":
            orchestrator_auto_remediate = self.auto_remediate_maintenance_alert_governance_escalation_remediations(
                dry_run=dry_run,
                limit=query_limit,
            )
            if not dry_run:
                remediated_orchestrator = bool(orchestrator_auto_remediate.executed)
        elif action == "auto_prune_runs":
            run_history_auto_prune = self.auto_prune_maintenance_alert_governance_escalation_remediation_auto_remediate_runs(
                dry_run=dry_run
            )
            if not dry_run and run_history_auto_prune.prune is not None:
                pruned_run_history = bool(
                    run_history_auto_prune.prune.pruned_count > 0
                    or run_history_auto_prune.prune.malformed_dropped_count > 0
                )

        executed = remediated_orchestrator or pruned_run_history
        digest_after = self.build_maintenance_alert_governance_escalation_remediation_auto_remediate_runs_digest(
            limit=query_limit
        )
        if dry_run:
            message = "dry_run"
        elif executed:
            message = "remediated"
        else:
            message = "no_action"

        response = BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateResponse(
            generated_at=_now_iso(),
            dry_run=bool(dry_run),
            limit=query_limit,
            action=action,
            executed=executed,
            remediated_orchestrator=remediated_orchestrator,
            pruned_run_history=pruned_run_history,
            orchestrator_auto_remediate=orchestrator_auto_remediate,
            run_history_auto_prune=run_history_auto_prune,
            digest_before=digest_before,
            digest_after=digest_after,
            message=message,
        )
        run_record = BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunRecord(
            run_id=_new_timestamped_id("bm-governance-escalation-remediation-orchestrator-runs-auto-remediate-"),
            generated_at=response.generated_at,
            dry_run=bool(dry_run),
            limit=query_limit,
            action=action,
            executed=executed,
            remediated_orchestrator=remediated_orchestrator,
            pruned_run_history=pruned_run_history,
            digest_before_message=digest_before.message,
            digest_after_message=digest_after.message,
            message=message,
        )
        with self._lock:
            self._append_governance_escalation_remediation_auto_remediate_run_auto_remediate_run_record(
                path=self._governance_escalation_remediation_auto_remediate_run_auto_remediate_runs_path(),
                record=run_record,
            )
        return response

    def list_maintenance_alert_governance_escalation_remediation_auto_remediate_run_auto_remediate_runs(
        self,
        *,
        limit: int = 100,
        cursor: str = "",
    ) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunListResponse:
        query_limit = max(0, int(limit))
        offset = _parse_cursor_offset(cursor)
        with self._lock:
            path = self._governance_escalation_remediation_auto_remediate_run_auto_remediate_runs_path()
            if not path.exists():
                return BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunListResponse(
                    limit=query_limit,
                    cursor=str(offset),
                    records=[],
                    message="no_records",
                )
            rows, malformed_line_count = (
                self._read_governance_escalation_remediation_auto_remediate_run_auto_remediate_run_records(path=path)
            )

        ordered_rows = self._order_governance_escalation_remediation_auto_remediate_run_auto_remediate_run_records(rows)
        total = len(ordered_rows)
        start = min(offset, total)
        end = min(total, start + query_limit) if query_limit > 0 else total
        window = ordered_rows[start:end]
        has_more = end < total
        next_cursor = str(end) if has_more else ""
        return BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunListResponse(
            limit=query_limit,
            cursor=str(start),
            next_cursor=next_cursor,
            has_more=has_more,
            total_records=total,
            malformed_line_count=malformed_line_count,
            records=window,
            message="ok",
        )

    def summarize_maintenance_alert_governance_escalation_remediation_auto_remediate_run_auto_remediate_runs(
        self,
        *,
        limit: int = 200,
    ) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunSummaryResponse:
        query_limit = max(0, int(limit))
        with self._lock:
            path = self._governance_escalation_remediation_auto_remediate_run_auto_remediate_runs_path()
            if not path.exists():
                return BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunSummaryResponse(
                    generated_at=_now_iso(),
                    limit=query_limit,
                    message="no_records",
                )
            rows, malformed_line_count = (
                self._read_governance_escalation_remediation_auto_remediate_run_auto_remediate_run_records(path=path)
            )

        ordered_rows = self._order_governance_escalation_remediation_auto_remediate_run_auto_remediate_run_records(rows)
        window = ordered_rows[:query_limit] if query_limit > 0 else ordered_rows
        return BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunSummaryResponse(
            generated_at=_now_iso(),
            limit=query_limit,
            total_records=len(ordered_rows),
            window_record_count=len(window),
            malformed_line_count=malformed_line_count,
            dry_run_count=sum(1 for item in window if item.dry_run),
            apply_count=sum(1 for item in window if not item.dry_run),
            executed_count=sum(1 for item in window if item.executed),
            remediated_orchestrator_count=sum(1 for item in window if item.remediated_orchestrator),
            pruned_run_history_count=sum(1 for item in window if item.pruned_run_history),
            latest_record=ordered_rows[0] if ordered_rows else None,
            message="ok",
        )

    def export_maintenance_alert_governance_escalation_remediation_auto_remediate_run_auto_remediate_runs(
        self,
        *,
        limit: int = 200,
        cursor: str = "",
    ) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunExportResponse:
        query_limit = max(0, int(limit))
        summary = self.summarize_maintenance_alert_governance_escalation_remediation_auto_remediate_run_auto_remediate_runs(
            limit=query_limit
        )
        page = self.list_maintenance_alert_governance_escalation_remediation_auto_remediate_run_auto_remediate_runs(
            limit=query_limit,
            cursor=cursor,
        )
        return BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunExportResponse(
            generated_at=_now_iso(),
            limit=query_limit,
            cursor=page.cursor,
            next_cursor=page.next_cursor,
            has_more=page.has_more,
            total_records=page.total_records,
            malformed_line_count=page.malformed_line_count,
            summary=summary,
            records=page.records,
            message="ok",
        )

    def prune_maintenance_alert_governance_escalation_remediation_auto_remediate_run_auto_remediate_runs(
        self,
        *,
        keep_last: int,
        dry_run: bool = True,
    ) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunPruneResponse:
        keep_count = max(0, int(keep_last))
        with self._lock:
            path = self._governance_escalation_remediation_auto_remediate_run_auto_remediate_runs_path()
            if not path.exists():
                return BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunPruneResponse(
                    generated_at=_now_iso(),
                    dry_run=bool(dry_run),
                    keep_last=keep_count,
                    message="no_records",
                )

            rows, malformed_candidate_count = (
                self._read_governance_escalation_remediation_auto_remediate_run_auto_remediate_run_records(path=path)
            )
            ordered_rows = self._order_governance_escalation_remediation_auto_remediate_run_auto_remediate_run_records(rows)
            kept = ordered_rows[:keep_count]
            candidates = ordered_rows[keep_count:]

            pruned_run_ids: list[str] = []
            malformed_dropped_count = 0
            if not dry_run:
                self._write_governance_escalation_remediation_auto_remediate_run_auto_remediate_run_records(
                    path=path,
                    records=kept,
                )
                pruned_run_ids = [item.run_id for item in candidates]
                malformed_dropped_count = malformed_candidate_count

        return BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunPruneResponse(
            generated_at=_now_iso(),
            dry_run=bool(dry_run),
            keep_last=keep_count,
            total_records_before=len(rows),
            kept_count=len(kept),
            candidate_count=len(candidates),
            pruned_count=len(pruned_run_ids),
            malformed_candidate_count=malformed_candidate_count,
            malformed_dropped_count=malformed_dropped_count,
            kept_run_ids=[item.run_id for item in kept],
            pruned_run_ids=pruned_run_ids,
            message="dry_run" if dry_run else "pruned",
        )

    def auto_prune_maintenance_alert_governance_escalation_remediation_auto_remediate_run_auto_remediate_runs(
        self,
        *,
        dry_run: bool = True,
    ) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoPruneResponse:
        policy = self._load_alert_governance_policy()
        trigger_count = (
            policy.governance_escalation_remediation_auto_remediate_run_auto_remediate_runs_prune_trigger_count
        )
        keep_last = policy.governance_escalation_remediation_auto_remediate_run_auto_remediate_runs_prune_keep_last

        with self._lock:
            path = self._governance_escalation_remediation_auto_remediate_run_auto_remediate_runs_path()
            if path.exists():
                rows, malformed_line_count = (
                    self._read_governance_escalation_remediation_auto_remediate_run_auto_remediate_run_records(path=path)
                )
            else:
                rows = []
                malformed_line_count = 0

        total_records = len(rows)
        should_prune = total_records > trigger_count or malformed_line_count > 0
        if not should_prune:
            return BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoPruneResponse(
                generated_at=_now_iso(),
                dry_run=bool(dry_run),
                trigger_count=trigger_count,
                keep_last=keep_last,
                total_records=total_records,
                malformed_line_count=malformed_line_count,
                should_prune=False,
                prune=None,
                message="below_threshold",
            )

        prune = self.prune_maintenance_alert_governance_escalation_remediation_auto_remediate_run_auto_remediate_runs(
            keep_last=keep_last,
            dry_run=dry_run,
        )
        return BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoPruneResponse(
            generated_at=_now_iso(),
            dry_run=bool(dry_run),
            trigger_count=trigger_count,
            keep_last=keep_last,
            total_records=total_records,
            malformed_line_count=malformed_line_count,
            should_prune=True,
            prune=prune,
            message="pruned" if not dry_run else "dry_run",
        )

    def build_maintenance_alert_governance_escalation_remediation_auto_remediate_run_auto_remediate_runs_digest(
        self,
        *,
        limit: int = 200,
    ) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunDigestResponse:
        query_limit = max(0, int(limit))
        summary = self.summarize_maintenance_alert_governance_escalation_remediation_auto_remediate_run_auto_remediate_runs(
            limit=query_limit
        )
        policy = self._load_alert_governance_policy()
        stale_threshold_seconds = max(
            0,
            int(policy.governance_escalation_remediation_auto_remediate_run_auto_remediate_runs_stale_seconds),
        )

        latest_record_age_seconds = -1.0
        is_stale = True
        if summary.latest_record is not None:
            parsed_latest = _parse_iso_utc(summary.latest_record.generated_at)
            if parsed_latest is not None:
                latest_record_age_seconds = max(0.0, (datetime.now(timezone.utc) - parsed_latest).total_seconds())
                is_stale = latest_record_age_seconds > float(stale_threshold_seconds)
            else:
                is_stale = True

        if summary.latest_record is None:
            recommended_action = "run_auto_remediation_orchestrator_runs"
            message = "no_records"
        elif summary.malformed_line_count > 0:
            recommended_action = "auto_prune_runs"
            message = "malformed_detected"
        elif (
            summary.total_records
            > policy.governance_escalation_remediation_auto_remediate_run_auto_remediate_runs_prune_trigger_count
        ):
            recommended_action = "auto_prune_runs"
            message = "above_prune_threshold"
        elif is_stale:
            recommended_action = "run_auto_remediation_orchestrator_runs"
            message = "stale"
        else:
            recommended_action = "observe"
            message = "ok"

        return BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunDigestResponse(
            generated_at=_now_iso(),
            stale_threshold_seconds=stale_threshold_seconds,
            latest_record_age_seconds=latest_record_age_seconds,
            is_stale=is_stale,
            recommended_action=recommended_action,
            summary=summary,
            message=message,
        )

    def auto_remediate_maintenance_alert_governance_escalation_remediation_auto_remediate_run_auto_remediate_runs(
        self,
        *,
        dry_run: bool = True,
        limit: int = 200,
    ) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateResponse:
        query_limit = max(0, int(limit))
        digest_before = self.build_maintenance_alert_governance_escalation_remediation_auto_remediate_run_auto_remediate_runs_digest(
            limit=query_limit
        )
        action = str(digest_before.recommended_action or "observe")

        remediated_orchestrator_runs = False
        pruned_run_history = False
        orchestrator_runs_auto_remediate: (
            BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateResponse | None
        ) = None
        run_history_auto_prune: (
            BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoPruneResponse | None
        ) = None

        if action == "run_auto_remediation_orchestrator_runs":
            orchestrator_runs_auto_remediate = (
                self.auto_remediate_maintenance_alert_governance_escalation_remediation_auto_remediate_runs(
                    dry_run=dry_run,
                    limit=query_limit,
                )
            )
            if not dry_run:
                remediated_orchestrator_runs = bool(orchestrator_runs_auto_remediate.executed)
        elif action == "auto_prune_runs":
            run_history_auto_prune = (
                self.auto_prune_maintenance_alert_governance_escalation_remediation_auto_remediate_run_auto_remediate_runs(
                    dry_run=dry_run,
                )
            )
            if not dry_run and run_history_auto_prune.prune is not None:
                pruned_run_history = bool(
                    run_history_auto_prune.prune.pruned_count > 0
                    or run_history_auto_prune.prune.malformed_dropped_count > 0
                )

        executed = remediated_orchestrator_runs or pruned_run_history
        digest_after = self.build_maintenance_alert_governance_escalation_remediation_auto_remediate_run_auto_remediate_runs_digest(
            limit=query_limit
        )
        if dry_run:
            message = "dry_run"
        elif executed:
            message = "remediated"
        else:
            message = "no_action"

        response = BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateResponse(
            generated_at=_now_iso(),
            dry_run=bool(dry_run),
            limit=query_limit,
            action=action,
            executed=executed,
            remediated_orchestrator_runs=remediated_orchestrator_runs,
            pruned_run_history=pruned_run_history,
            orchestrator_runs_auto_remediate=orchestrator_runs_auto_remediate,
            run_history_auto_prune=run_history_auto_prune,
            digest_before=digest_before,
            digest_after=digest_after,
            message=message,
        )
        run_record = BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateRunRecord(
            run_id=_new_timestamped_id("bm-governance-escalation-remediation-orchestrator-runs-auto-remediate-runs-auto-remediate-"),
            generated_at=response.generated_at,
            dry_run=bool(dry_run),
            limit=query_limit,
            action=action,
            executed=executed,
            remediated_orchestrator_runs=remediated_orchestrator_runs,
            pruned_run_history=pruned_run_history,
            digest_before_message=digest_before.message,
            digest_after_message=digest_after.message,
            message=message,
        )
        with self._lock:
            self._append_governance_escalation_remediation_auto_remediate_run_auto_remediate_run_auto_remediate_run_record(
                path=self._governance_escalation_remediation_auto_remediate_run_auto_remediate_runs_auto_remediate_runs_path(),
                record=run_record,
            )
        return response

    def list_maintenance_alert_governance_escalation_remediation_auto_remediate_run_auto_remediate_runs_auto_remediate_runs(
        self,
        *,
        limit: int = 100,
        cursor: str = "",
    ) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateRunListResponse:
        query_limit = max(0, int(limit))
        offset = _parse_cursor_offset(cursor)
        with self._lock:
            path = self._governance_escalation_remediation_auto_remediate_run_auto_remediate_runs_auto_remediate_runs_path()
            if not path.exists():
                return BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateRunListResponse(
                    limit=query_limit,
                    cursor=str(offset),
                    records=[],
                    message="no_records",
                )
            rows, malformed_line_count = (
                self._read_governance_escalation_remediation_auto_remediate_run_auto_remediate_run_auto_remediate_run_records(
                    path=path
                )
            )

        ordered_rows = (
            self._order_governance_escalation_remediation_auto_remediate_run_auto_remediate_run_auto_remediate_run_records(
                rows
            )
        )
        total = len(ordered_rows)
        start = min(offset, total)
        end = min(total, start + query_limit) if query_limit > 0 else total
        window = ordered_rows[start:end]
        has_more = end < total
        next_cursor = str(end) if has_more else ""
        return BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateRunListResponse(
            limit=query_limit,
            cursor=str(start),
            next_cursor=next_cursor,
            has_more=has_more,
            total_records=total,
            malformed_line_count=malformed_line_count,
            records=window,
            message="ok",
        )

    def summarize_maintenance_alert_governance_escalation_remediation_auto_remediate_run_auto_remediate_runs_auto_remediate_runs(
        self,
        *,
        limit: int = 200,
    ) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateRunSummaryResponse:
        query_limit = max(0, int(limit))
        with self._lock:
            path = self._governance_escalation_remediation_auto_remediate_run_auto_remediate_runs_auto_remediate_runs_path()
            if not path.exists():
                return BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateRunSummaryResponse(
                    generated_at=_now_iso(),
                    limit=query_limit,
                    message="no_records",
                )
            rows, malformed_line_count = (
                self._read_governance_escalation_remediation_auto_remediate_run_auto_remediate_run_auto_remediate_run_records(
                    path=path
                )
            )

        ordered_rows = (
            self._order_governance_escalation_remediation_auto_remediate_run_auto_remediate_run_auto_remediate_run_records(
                rows
            )
        )
        window = ordered_rows[:query_limit] if query_limit > 0 else ordered_rows
        return BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateRunSummaryResponse(
            generated_at=_now_iso(),
            limit=query_limit,
            total_records=len(ordered_rows),
            window_record_count=len(window),
            malformed_line_count=malformed_line_count,
            dry_run_count=sum(1 for item in window if item.dry_run),
            apply_count=sum(1 for item in window if not item.dry_run),
            executed_count=sum(1 for item in window if item.executed),
            remediated_orchestrator_runs_count=sum(1 for item in window if item.remediated_orchestrator_runs),
            pruned_run_history_count=sum(1 for item in window if item.pruned_run_history),
            latest_record=ordered_rows[0] if ordered_rows else None,
            message="ok",
        )

    def export_maintenance_alert_governance_escalation_remediation_auto_remediate_run_auto_remediate_runs_auto_remediate_runs(
        self,
        *,
        limit: int = 200,
        cursor: str = "",
    ) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateRunExportResponse:
        query_limit = max(0, int(limit))
        summary = (
            self.summarize_maintenance_alert_governance_escalation_remediation_auto_remediate_run_auto_remediate_runs_auto_remediate_runs(
                limit=query_limit
            )
        )
        page = (
            self.list_maintenance_alert_governance_escalation_remediation_auto_remediate_run_auto_remediate_runs_auto_remediate_runs(
                limit=query_limit,
                cursor=cursor,
            )
        )
        return BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateRunExportResponse(
            generated_at=_now_iso(),
            limit=query_limit,
            cursor=page.cursor,
            next_cursor=page.next_cursor,
            has_more=page.has_more,
            total_records=page.total_records,
            malformed_line_count=page.malformed_line_count,
            summary=summary,
            records=page.records,
            message="ok",
        )

    def prune_maintenance_alert_governance_escalation_remediation_auto_remediate_run_auto_remediate_runs_auto_remediate_runs(
        self,
        *,
        keep_last: int,
        dry_run: bool = True,
    ) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateRunPruneResponse:
        keep_count = max(0, int(keep_last))
        with self._lock:
            path = self._governance_escalation_remediation_auto_remediate_run_auto_remediate_runs_auto_remediate_runs_path()
            if not path.exists():
                return BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateRunPruneResponse(
                    generated_at=_now_iso(),
                    dry_run=bool(dry_run),
                    keep_last=keep_count,
                    message="no_records",
                )

            rows, malformed_candidate_count = (
                self._read_governance_escalation_remediation_auto_remediate_run_auto_remediate_run_auto_remediate_run_records(
                    path=path
                )
            )
            ordered_rows = (
                self._order_governance_escalation_remediation_auto_remediate_run_auto_remediate_run_auto_remediate_run_records(
                    rows
                )
            )
            kept = ordered_rows[:keep_count]
            candidates = ordered_rows[keep_count:]

            pruned_run_ids: list[str] = []
            malformed_dropped_count = 0
            if not dry_run:
                self._write_governance_escalation_remediation_auto_remediate_run_auto_remediate_run_auto_remediate_run_records(
                    path=path,
                    records=kept,
                )
                pruned_run_ids = [item.run_id for item in candidates]
                malformed_dropped_count = malformed_candidate_count

        return BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateRunPruneResponse(
            generated_at=_now_iso(),
            dry_run=bool(dry_run),
            keep_last=keep_count,
            total_records_before=len(rows),
            kept_count=len(kept),
            candidate_count=len(candidates),
            pruned_count=len(pruned_run_ids),
            malformed_candidate_count=malformed_candidate_count,
            malformed_dropped_count=malformed_dropped_count,
            kept_run_ids=[item.run_id for item in kept],
            pruned_run_ids=pruned_run_ids,
            message="dry_run" if dry_run else "pruned",
        )

    def auto_remediate_maintenance_alert_governance_runs(
        self,
        *,
        dry_run: bool = True,
        limit: int = 200,
        alert_limit: int = 200,
        archive_limit: int = 200,
    ) -> BenchmarkMaintenanceAlertGovernanceRunAutoRemediateResponse:
        query_limit = max(0, int(limit))
        resolved_alert_limit = max(0, int(alert_limit))
        resolved_archive_limit = max(0, int(archive_limit))

        digest_before = self.build_maintenance_alert_governance_runs_digest(limit=query_limit)
        action = str(digest_before.recommended_action or "observe")

        executed = False
        escalation_required = False
        escalation_reason = ""
        escalation_event: BenchmarkMaintenanceAlertGovernanceEscalationEvent | None = None
        governance_run: BenchmarkMaintenanceAlertGovernanceRunResponse | None = None
        auto_prune: BenchmarkMaintenanceAlertGovernanceRunAutoPruneResponse | None = None

        if action == "retry_latest_failed_run":
            latest_failed = digest_before.summary.latest_failed_run
            if latest_failed is not None and not dry_run:
                governance_run = self.run_maintenance_alert_governance(
                    dry_run=False,
                    alert_limit=resolved_alert_limit,
                    archive_limit=resolved_archive_limit,
                    retry_run_id=latest_failed.run_id,
                )
                executed = True
        elif action == "auto_prune_runs":
            auto_prune = self.auto_prune_maintenance_alert_governance_runs(dry_run=dry_run)
            executed = bool(not dry_run and auto_prune.prune is not None and auto_prune.prune.pruned_count > 0)
        elif action == "execute_governance_run":
            if not dry_run:
                governance_run = self.run_maintenance_alert_governance(
                    dry_run=False,
                    alert_limit=resolved_alert_limit,
                    archive_limit=resolved_archive_limit,
                )
                executed = True
        elif action == "escalate_failed_run":
            escalation_required = True
            escalation_reason = self._resolve_governance_escalation_reason(digest=digest_before)
            if not dry_run:
                emitted = self.emit_maintenance_alert_governance_escalation(limit=query_limit, source="auto_remediate")
                escalation_event = emitted.event

        digest_after = self.build_maintenance_alert_governance_runs_digest(limit=query_limit)
        if dry_run:
            message = "dry_run"
        elif escalation_required:
            message = "escalation_required"
        elif executed:
            message = "remediated"
        else:
            message = "no_action"

        return BenchmarkMaintenanceAlertGovernanceRunAutoRemediateResponse(
            generated_at=_now_iso(),
            dry_run=bool(dry_run),
            limit=query_limit,
            alert_limit=resolved_alert_limit,
            archive_limit=resolved_archive_limit,
            action=action,
            executed=executed,
            escalation_required=escalation_required,
            escalation_reason=escalation_reason,
            escalation_event=escalation_event,
            governance_run=governance_run,
            auto_prune=auto_prune,
            digest_before=digest_before,
            digest_after=digest_after,
            message=message,
        )

    def prune_maintenance_alert_governance_runs(
        self,
        *,
        keep_last: int,
        dry_run: bool = True,
    ) -> BenchmarkMaintenanceAlertGovernanceRunPruneResponse:
        keep_count = max(0, int(keep_last))
        with self._lock:
            path = self._governance_runs_path()
            if not path.exists():
                return BenchmarkMaintenanceAlertGovernanceRunPruneResponse(
                    generated_at=_now_iso(),
                    dry_run=bool(dry_run),
                    keep_last=keep_count,
                    message="no_runs",
                )

            rows, malformed_candidate_count = self._read_governance_run_records(path=path)
            ordered_rows = self._order_governance_run_records(rows)
            kept = ordered_rows[:keep_count]
            candidates = ordered_rows[keep_count:]

            pruned_run_ids: list[str] = []
            malformed_dropped_count = 0
            if not dry_run:
                self._write_governance_run_records(path=path, records=kept)
                pruned_run_ids = [item.run_id for item in candidates]
                malformed_dropped_count = malformed_candidate_count

        return BenchmarkMaintenanceAlertGovernanceRunPruneResponse(
            generated_at=_now_iso(),
            dry_run=bool(dry_run),
            keep_last=keep_count,
            total_runs_before=len(rows),
            kept_count=len(kept),
            candidate_count=len(candidates),
            pruned_count=len(pruned_run_ids),
            malformed_candidate_count=malformed_candidate_count,
            malformed_dropped_count=malformed_dropped_count,
            kept_run_ids=[item.run_id for item in kept],
            pruned_run_ids=pruned_run_ids,
            message="dry_run" if dry_run else "pruned",
        )

    def build_maintenance_alert_digest(self, *, limit: int = 200) -> BenchmarkMaintenanceAlertDigestResponse:
        current_alert = self.build_maintenance_alert(limit=limit)
        summary = self.summarize_maintenance_alerts(limit=limit)
        stale_threshold_seconds = _env_int("AA_V7_BENCH_ALERT_STALE_SECONDS", 900, low=0)

        latest_event_age_seconds = -1.0
        is_stale = True
        if summary.latest_event is not None:
            parsed_latest = _parse_iso_utc(summary.latest_event.generated_at)
            if parsed_latest is not None:
                latest_event_age_seconds = max(0.0, (datetime.now(timezone.utc) - parsed_latest).total_seconds())
                is_stale = latest_event_age_seconds > stale_threshold_seconds
            else:
                is_stale = True

        if current_alert.should_page:
            recommended_action = "page_oncall"
        elif current_alert.should_ticket:
            recommended_action = "create_ticket"
        elif is_stale:
            recommended_action = "emit_fresh_alert"
        elif summary.malformed_line_count > 0:
            recommended_action = "clean_alert_log"
        else:
            recommended_action = "observe"

        return BenchmarkMaintenanceAlertDigestResponse(
            generated_at=_now_iso(),
            stale_threshold_seconds=stale_threshold_seconds,
            latest_event_age_seconds=latest_event_age_seconds,
            is_stale=is_stale,
            recommended_action=recommended_action,
            current_alert=current_alert,
            summary=summary,
            message="ok" if summary.latest_event is not None else "no_alert_event",
        )

    def export_maintenance_alerts(
        self,
        *,
        limit: int = 200,
        cursor: str = "",
    ) -> BenchmarkMaintenanceAlertExportResponse:
        query_limit = max(0, int(limit))
        digest = self.build_maintenance_alert_digest(limit=query_limit)
        page = self.list_maintenance_alerts(limit=query_limit, cursor=cursor)
        return BenchmarkMaintenanceAlertExportResponse(
            generated_at=_now_iso(),
            limit=query_limit,
            cursor=page.cursor,
            next_cursor=page.next_cursor,
            has_more=page.has_more,
            total_valid_events=page.total_valid_events,
            malformed_line_count=page.malformed_line_count,
            digest=digest,
            alerts=page.alerts,
            message="ok",
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

    def _alerts_path(self) -> Path:
        return self.version_root / "_maintenance_alerts.jsonl"

    def _alerts_archive_dir(self) -> Path:
        return self.version_root / "_maintenance_alerts_archive"

    def _governance_runs_path(self) -> Path:
        return self.version_root / "_maintenance_alert_governance_runs.jsonl"

    def _governance_escalations_path(self) -> Path:
        return self.version_root / "_maintenance_alert_governance_escalations.jsonl"

    def _governance_escalation_remediations_path(self) -> Path:
        return self.version_root / "_maintenance_alert_governance_escalation_remediations.jsonl"

    def _governance_escalation_remediation_auto_remediate_runs_path(self) -> Path:
        return self.version_root / "_maintenance_alert_governance_escalation_remediation_auto_remediate_runs.jsonl"

    def _governance_escalation_remediation_auto_remediate_run_auto_remediate_runs_path(self) -> Path:
        return self.version_root / "_maintenance_alert_governance_escalation_remediation_auto_remediate_run_auto_remediate_runs.jsonl"

    def _governance_escalation_remediation_auto_remediate_run_auto_remediate_runs_auto_remediate_runs_path(self) -> Path:
        return (
            self.version_root
            / "_maintenance_alert_governance_escalation_remediation_auto_remediate_run_auto_remediate_runs_auto_remediate_runs.jsonl"
        )

    def _next_governance_run_id(self) -> str:
        return _new_timestamped_id("bm-governance-run-")

    def _governance_run_fingerprint(
        self,
        *,
        dry_run: bool,
        alert_limit: int,
        archive_limit: int,
        retry_run_id: str,
    ) -> str:
        payload = {
            "dry_run": bool(dry_run),
            "alert_limit": int(alert_limit),
            "archive_limit": int(archive_limit),
            "retry_run_id": str(retry_run_id or ""),
        }
        canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def _append_governance_run_record(
        self,
        *,
        path: Path,
        record: BenchmarkMaintenanceAlertGovernanceRunRecord,
    ) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record.model_dump(mode="json"), ensure_ascii=False))
            handle.write("\n")

    def _append_governance_escalation_remediation_run_record(
        self,
        *,
        path: Path,
        record: BenchmarkMaintenanceAlertGovernanceEscalationRemediationRunRecord,
    ) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record.model_dump(mode="json"), ensure_ascii=False))
            handle.write("\n")

    def _append_governance_escalation_remediation_auto_remediate_run_record(
        self,
        *,
        path: Path,
        record: BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunRecord,
    ) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record.model_dump(mode="json"), ensure_ascii=False))
            handle.write("\n")

    def _append_governance_escalation_remediation_auto_remediate_run_auto_remediate_run_record(
        self,
        *,
        path: Path,
        record: BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunRecord,
    ) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record.model_dump(mode="json"), ensure_ascii=False))
            handle.write("\n")

    def _append_governance_escalation_remediation_auto_remediate_run_auto_remediate_run_auto_remediate_run_record(
        self,
        *,
        path: Path,
        record: BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateRunRecord,
    ) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record.model_dump(mode="json"), ensure_ascii=False))
            handle.write("\n")

    def _write_governance_run_records(
        self,
        *,
        path: Path,
        records: list[BenchmarkMaintenanceAlertGovernanceRunRecord],
    ) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = path.with_suffix(f"{path.suffix}.tmp")
        serialized = [json.dumps(item.model_dump(mode="json"), ensure_ascii=False) for item in records]
        payload = "\n".join(serialized)
        if payload:
            payload += "\n"
        temp_path.write_text(payload, encoding="utf-8")
        temp_path.replace(path)

    def _write_governance_escalation_remediation_run_records(
        self,
        *,
        path: Path,
        records: list[BenchmarkMaintenanceAlertGovernanceEscalationRemediationRunRecord],
    ) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = path.with_suffix(f"{path.suffix}.tmp")
        serialized = [json.dumps(item.model_dump(mode="json"), ensure_ascii=False) for item in records]
        payload = "\n".join(serialized)
        if payload:
            payload += "\n"
        temp_path.write_text(payload, encoding="utf-8")
        temp_path.replace(path)

    def _write_governance_escalation_remediation_auto_remediate_run_records(
        self,
        *,
        path: Path,
        records: list[BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunRecord],
    ) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = path.with_suffix(f"{path.suffix}.tmp")
        serialized = [json.dumps(item.model_dump(mode="json"), ensure_ascii=False) for item in records]
        payload = "\n".join(serialized)
        if payload:
            payload += "\n"
        temp_path.write_text(payload, encoding="utf-8")
        temp_path.replace(path)

    def _write_governance_escalation_remediation_auto_remediate_run_auto_remediate_run_records(
        self,
        *,
        path: Path,
        records: list[BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunRecord],
    ) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = path.with_suffix(f"{path.suffix}.tmp")
        serialized = [json.dumps(item.model_dump(mode="json"), ensure_ascii=False) for item in records]
        payload = "\n".join(serialized)
        if payload:
            payload += "\n"
        temp_path.write_text(payload, encoding="utf-8")
        temp_path.replace(path)

    def _write_governance_escalation_remediation_auto_remediate_run_auto_remediate_run_auto_remediate_run_records(
        self,
        *,
        path: Path,
        records: list[
            BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateRunRecord
        ],
    ) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = path.with_suffix(f"{path.suffix}.tmp")
        serialized = [json.dumps(item.model_dump(mode="json"), ensure_ascii=False) for item in records]
        payload = "\n".join(serialized)
        if payload:
            payload += "\n"
        temp_path.write_text(payload, encoding="utf-8")
        temp_path.replace(path)

    def _read_governance_escalation_remediation_auto_remediate_run_records(
        self,
        *,
        path: Path,
    ) -> tuple[list[BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunRecord], int]:
        rows: list[BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunRecord] = []
        malformed_count = 0
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except Exception:
                malformed_count += 1
                continue
            if not isinstance(payload, dict):
                malformed_count += 1
                continue
            try:
                rows.append(BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunRecord.model_validate(payload))
            except Exception:
                malformed_count += 1
        return rows, malformed_count

    def _read_governance_escalation_remediation_auto_remediate_run_auto_remediate_run_records(
        self,
        *,
        path: Path,
    ) -> tuple[list[BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunRecord], int]:
        rows: list[BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunRecord] = []
        malformed_count = 0
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except Exception:
                malformed_count += 1
                continue
            if not isinstance(payload, dict):
                malformed_count += 1
                continue
            try:
                rows.append(
                    BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunRecord.model_validate(
                        payload
                    )
                )
            except Exception:
                malformed_count += 1
        return rows, malformed_count

    def _read_governance_escalation_remediation_auto_remediate_run_auto_remediate_run_auto_remediate_run_records(
        self,
        *,
        path: Path,
    ) -> tuple[list[BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateRunRecord], int]:
        rows: list[BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateRunRecord] = []
        malformed_count = 0
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except Exception:
                malformed_count += 1
                continue
            if not isinstance(payload, dict):
                malformed_count += 1
                continue
            try:
                rows.append(
                    BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateRunRecord.model_validate(
                        payload
                    )
                )
            except Exception:
                malformed_count += 1
        return rows, malformed_count

    def _read_governance_run_records(self, *, path: Path) -> tuple[list[BenchmarkMaintenanceAlertGovernanceRunRecord], int]:
        rows: list[BenchmarkMaintenanceAlertGovernanceRunRecord] = []
        malformed_count = 0
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except Exception:
                malformed_count += 1
                continue
            if not isinstance(payload, dict):
                malformed_count += 1
                continue
            try:
                rows.append(BenchmarkMaintenanceAlertGovernanceRunRecord.model_validate(payload))
            except Exception:
                malformed_count += 1
        return rows, malformed_count

    def _order_governance_run_records(
        self,
        records: list[BenchmarkMaintenanceAlertGovernanceRunRecord],
    ) -> list[BenchmarkMaintenanceAlertGovernanceRunRecord]:
        indexed = list(enumerate(records))
        indexed.sort(
            key=lambda item: (
                item[1].generated_at,
                item[1].completed_at,
                item[1].attempt,
                item[1].run_id,
                item[0],
            ),
            reverse=True,
        )
        return [item[1] for item in indexed]

    def _order_governance_escalation_events(
        self,
        events: list[BenchmarkMaintenanceAlertGovernanceEscalationEvent],
    ) -> list[BenchmarkMaintenanceAlertGovernanceEscalationEvent]:
        indexed = list(enumerate(events))
        indexed.sort(
            key=lambda item: (
                item[1].generated_at,
                item[1].event_id,
                item[0],
            ),
            reverse=True,
        )
        return [item[1] for item in indexed]

    def _order_governance_escalation_remediation_run_records(
        self,
        records: list[BenchmarkMaintenanceAlertGovernanceEscalationRemediationRunRecord],
    ) -> list[BenchmarkMaintenanceAlertGovernanceEscalationRemediationRunRecord]:
        indexed = list(enumerate(records))
        indexed.sort(
            key=lambda item: (
                item[1].generated_at,
                item[1].run_id,
                item[0],
            ),
            reverse=True,
        )
        return [item[1] for item in indexed]

    def _order_governance_escalation_remediation_auto_remediate_run_records(
        self,
        records: list[BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunRecord],
    ) -> list[BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunRecord]:
        indexed = list(enumerate(records))
        indexed.sort(
            key=lambda item: (
                item[1].generated_at,
                item[1].run_id,
                item[0],
            ),
            reverse=True,
        )
        return [item[1] for item in indexed]

    def _order_governance_escalation_remediation_auto_remediate_run_auto_remediate_run_records(
        self,
        records: list[BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunRecord],
    ) -> list[BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunRecord]:
        indexed = list(enumerate(records))
        indexed.sort(
            key=lambda item: (
                item[1].generated_at,
                item[1].run_id,
                item[0],
            ),
            reverse=True,
        )
        return [item[1] for item in indexed]

    def _order_governance_escalation_remediation_auto_remediate_run_auto_remediate_run_auto_remediate_run_records(
        self,
        records: list[
            BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateRunRecord
        ],
    ) -> list[BenchmarkMaintenanceAlertGovernanceEscalationRemediationAutoRemediateRunAutoRemediateRunAutoRemediateRunRecord]:
        indexed = list(enumerate(records))
        indexed.sort(
            key=lambda item: (
                item[1].generated_at,
                item[1].run_id,
                item[0],
            ),
            reverse=True,
        )
        return [item[1] for item in indexed]

    def _write_alert_events(self, *, path: Path, events: list[BenchmarkMaintenanceAlertEvent]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = path.with_suffix(f"{path.suffix}.tmp")
        serialized = [json.dumps(item.model_dump(mode="json"), ensure_ascii=False) for item in events]
        payload = "\n".join(serialized)
        if payload:
            payload += "\n"
        temp_path.write_text(payload, encoding="utf-8")
        temp_path.replace(path)

    def _read_alert_events(self, *, path: Path) -> tuple[list[BenchmarkMaintenanceAlertEvent], int]:
        rows: list[BenchmarkMaintenanceAlertEvent] = []
        malformed_count = 0
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except Exception:
                malformed_count += 1
                continue
            if not isinstance(payload, dict):
                malformed_count += 1
                continue
            try:
                rows.append(BenchmarkMaintenanceAlertEvent.model_validate(payload))
            except Exception:
                malformed_count += 1
        return rows, malformed_count

    def _write_governance_escalation_events(
        self,
        *,
        path: Path,
        events: list[BenchmarkMaintenanceAlertGovernanceEscalationEvent],
    ) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = path.with_suffix(f"{path.suffix}.tmp")
        serialized = [json.dumps(item.model_dump(mode="json"), ensure_ascii=False) for item in events]
        payload = "\n".join(serialized)
        if payload:
            payload += "\n"
        temp_path.write_text(payload, encoding="utf-8")
        temp_path.replace(path)

    def _read_governance_escalation_events(
        self,
        *,
        path: Path,
    ) -> tuple[list[BenchmarkMaintenanceAlertGovernanceEscalationEvent], int]:
        rows: list[BenchmarkMaintenanceAlertGovernanceEscalationEvent] = []
        malformed_count = 0
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except Exception:
                malformed_count += 1
                continue
            if not isinstance(payload, dict):
                malformed_count += 1
                continue
            try:
                rows.append(BenchmarkMaintenanceAlertGovernanceEscalationEvent.model_validate(payload))
            except Exception:
                malformed_count += 1
        return rows, malformed_count

    def _read_governance_escalation_remediation_run_records(
        self,
        *,
        path: Path,
    ) -> tuple[list[BenchmarkMaintenanceAlertGovernanceEscalationRemediationRunRecord], int]:
        rows: list[BenchmarkMaintenanceAlertGovernanceEscalationRemediationRunRecord] = []
        malformed_count = 0
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except Exception:
                malformed_count += 1
                continue
            if not isinstance(payload, dict):
                malformed_count += 1
                continue
            try:
                rows.append(BenchmarkMaintenanceAlertGovernanceEscalationRemediationRunRecord.model_validate(payload))
            except Exception:
                malformed_count += 1
        return rows, malformed_count

    def _resolve_governance_escalation_reason(
        self,
        *,
        digest: BenchmarkMaintenanceAlertGovernanceRunDigestResponse,
    ) -> str:
        if digest.message == "consecutive_failure_streak_exhausted":
            return (
                f"consecutive_failures_{digest.summary.consecutive_failed_runs}"
                f"_reached_limit_{digest.escalation_failure_streak_limit}"
            )
        if digest.summary.latest_failed_run is not None:
            return f"retry_exhausted_at_attempt_{digest.summary.latest_failed_run.attempt}"
        return "retry_exhausted"

    def _load_maintenance_sla_policy(self) -> BenchmarkMaintenanceSlaPolicy:
        return BenchmarkMaintenanceSlaPolicy(
            max_failed_integrity=_env_int("AA_V7_BENCH_SLA_MAX_FAILED_INTEGRITY", 0, low=0),
            max_malformed_files=_env_int("AA_V7_BENCH_SLA_MAX_MALFORMED_FILES", 0, low=0),
            max_unverified=_env_int("AA_V7_BENCH_SLA_MAX_UNVERIFIED", 0, low=0),
            max_version_count_warn=_env_int("AA_V7_BENCH_SLA_MAX_VERSION_COUNT_WARN", 500, low=0),
            max_version_count_critical=_env_int("AA_V7_BENCH_SLA_MAX_VERSION_COUNT_CRITICAL", 2000, low=0),
            page_on_critical=_env_bool("AA_V7_BENCH_SLA_PAGE_ON_CRITICAL", True),
            ticket_on_warn=_env_bool("AA_V7_BENCH_SLA_TICKET_ON_WARN", True),
        )

    def _load_alert_governance_policy(self) -> BenchmarkMaintenanceAlertGovernancePolicy:
        return BenchmarkMaintenanceAlertGovernancePolicy(
            archive_trigger_count=_env_int("AA_V7_BENCH_ALERT_ARCHIVE_TRIGGER_COUNT", 10000, low=0),
            archive_keep_last=_env_int("AA_V7_BENCH_ALERT_ARCHIVE_KEEP_LAST", 5000, low=0),
            archive_shard_size=_env_int("AA_V7_BENCH_ALERT_ARCHIVE_SHARD_SIZE", 1000, low=1),
            archive_ttl_days=_env_int("AA_V7_BENCH_ALERT_ARCHIVE_TTL_DAYS", 30, low=0),
            archive_max_shard_files=_env_int("AA_V7_BENCH_ALERT_ARCHIVE_MAX_SHARD_FILES", 5000, low=0),
            governance_runs_prune_trigger_count=_env_int("AA_V7_BENCH_GOVERNANCE_RUNS_PRUNE_TRIGGER_COUNT", 10000, low=0),
            governance_runs_prune_keep_last=_env_int("AA_V7_BENCH_GOVERNANCE_RUNS_PRUNE_KEEP_LAST", 5000, low=0),
            governance_escalations_prune_trigger_count=_env_int(
                "AA_V7_BENCH_GOVERNANCE_ESCALATIONS_PRUNE_TRIGGER_COUNT",
                10000,
                low=0,
            ),
            governance_escalations_prune_keep_last=_env_int(
                "AA_V7_BENCH_GOVERNANCE_ESCALATIONS_PRUNE_KEEP_LAST",
                5000,
                low=0,
            ),
            governance_escalation_remediations_prune_trigger_count=_env_int(
                "AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATIONS_PRUNE_TRIGGER_COUNT",
                10000,
                low=0,
            ),
            governance_escalation_remediations_prune_keep_last=_env_int(
                "AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATIONS_PRUNE_KEEP_LAST",
                5000,
                low=0,
            ),
            governance_escalation_remediation_auto_remediate_runs_prune_trigger_count=_env_int(
                "AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATION_AUTO_REMEDIATE_RUNS_PRUNE_TRIGGER_COUNT",
                10000,
                low=0,
            ),
            governance_escalation_remediation_auto_remediate_runs_prune_keep_last=_env_int(
                "AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATION_AUTO_REMEDIATE_RUNS_PRUNE_KEEP_LAST",
                5000,
                low=0,
            ),
            governance_escalation_remediation_auto_remediate_run_auto_remediate_runs_prune_trigger_count=_env_int(
                "AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATION_AUTO_REMEDIATE_RUN_AUTO_REMEDIATE_RUNS_PRUNE_TRIGGER_COUNT",
                10000,
                low=0,
            ),
            governance_escalation_remediation_auto_remediate_run_auto_remediate_runs_prune_keep_last=_env_int(
                "AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATION_AUTO_REMEDIATE_RUN_AUTO_REMEDIATE_RUNS_PRUNE_KEEP_LAST",
                5000,
                low=0,
            ),
            governance_escalation_remediation_auto_remediate_run_auto_remediate_runs_stale_seconds=_env_int(
                "AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATION_AUTO_REMEDIATE_RUN_AUTO_REMEDIATE_RUNS_STALE_SECONDS",
                900,
                low=0,
            ),
            governance_escalation_remediation_auto_remediate_runs_stale_seconds=_env_int(
                "AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATION_AUTO_REMEDIATE_RUNS_STALE_SECONDS",
                900,
                low=0,
            ),
            governance_escalation_remediations_stale_seconds=_env_int(
                "AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATIONS_STALE_SECONDS",
                900,
                low=0,
            ),
            governance_escalations_emit_cooldown_seconds=_env_int(
                "AA_V7_BENCH_GOVERNANCE_ESCALATIONS_EMIT_COOLDOWN_SECONDS",
                300,
                low=0,
            ),
            governance_runs_max_retry_attempts=_env_int("AA_V7_BENCH_GOVERNANCE_RUNS_MAX_RETRY_ATTEMPTS", 3, low=1),
            governance_runs_escalation_failure_streak=_env_int(
                "AA_V7_BENCH_GOVERNANCE_RUNS_ESCALATION_FAILURE_STREAK",
                3,
                low=1,
            ),
            stale_threshold_seconds=_env_int("AA_V7_BENCH_ALERT_STALE_SECONDS", 900, low=0),
        )

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

    def _unique_target_path(self, directory: Path, name: str) -> Path:
        target = directory / name
        if not target.exists():
            return target
        stem = target.stem
        suffix = target.suffix
        index = 1
        while True:
            candidate = directory / f"{stem}-{index}{suffix}"
            if not candidate.exists():
                return candidate
            index += 1

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
