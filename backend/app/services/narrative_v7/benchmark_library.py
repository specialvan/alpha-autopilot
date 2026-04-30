from __future__ import annotations

from .benchmark_store import V7BenchmarkStore
from .schemas import (
    BenchmarkAuditExportResponse,
    BenchmarkIngestRequest,
    BenchmarkIngestResponse,
    BenchmarkMaintenanceAlertResponse,
    BenchmarkMaintenanceAlertEmitResponse,
    BenchmarkMaintenanceAlertDigestResponse,
    BenchmarkMaintenanceAlertArchiveResponse,
    BenchmarkMaintenanceAlertArchiveListResponse,
    BenchmarkMaintenanceAlertArchiveReadResponse,
    BenchmarkMaintenanceAlertArchiveCleanupResponse,
    BenchmarkMaintenanceAlertAutoArchiveResponse,
    BenchmarkMaintenanceAlertGovernanceReportResponse,
    BenchmarkMaintenanceAlertGovernanceRunListResponse,
    BenchmarkMaintenanceAlertGovernanceRunExportResponse,
    BenchmarkMaintenanceAlertGovernanceRunAutoPruneResponse,
    BenchmarkMaintenanceAlertGovernanceRunDigestResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationEmitResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationListResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationSummaryResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationExportResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationPruneResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationAutoPruneResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationDigestResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationAutoRemediateResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationListResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationSummaryResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationExportResponse,
    BenchmarkMaintenanceAlertGovernanceEscalationRemediationPruneResponse,
    BenchmarkMaintenanceAlertGovernanceRunAutoRemediateResponse,
    BenchmarkMaintenanceAlertGovernanceRunPruneResponse,
    BenchmarkMaintenanceAlertGovernanceRunResponse,
    BenchmarkMaintenanceAlertGovernanceRunSummaryResponse,
    BenchmarkMaintenanceAlertExportResponse,
    BenchmarkMaintenanceAlertListResponse,
    BenchmarkMaintenanceAlertPruneResponse,
    BenchmarkMaintenanceAlertSummaryResponse,
    BenchmarkMaintenanceReportResponse,
    BenchmarkVersionAutoRemediateResponse,
    BenchmarkQueryRequest,
    BenchmarkQueryResponse,
    BenchmarkRestoreResponse,
    BenchmarkVersionDiffResponse,
    BenchmarkVersionHealthResponse,
    BenchmarkVersionPruneResponse,
    BenchmarkVersionRepairResponse,
    BenchmarkVersionRecord,
)


class BenchmarkLibrary:
    def __init__(self, *, store: V7BenchmarkStore) -> None:
        self._store = store

    def ingest_sample(self, payload: BenchmarkIngestRequest) -> BenchmarkIngestResponse:
        return self._store.ingest(payload)

    def query_benchmark(self, payload: BenchmarkQueryRequest) -> BenchmarkQueryResponse:
        return self._store.query(payload)

    def retract_sample(self, book_id: str) -> bool:
        return self._store.retract(book_id)

    def list_versions(self, *, limit: int = 20) -> list[BenchmarkVersionRecord]:
        return self._store.list_versions(limit=limit)

    def restore_version(self, version: str) -> BenchmarkRestoreResponse:
        return self._store.restore(version)

    def compare_versions(self, *, base_version: str, target_version: str) -> BenchmarkVersionDiffResponse:
        return self._store.compare_versions(base_version=base_version, target_version=target_version)

    def export_audit(self, *, limit: int = 50) -> BenchmarkAuditExportResponse:
        return self._store.export_audit(limit=limit)

    def prune_versions(self, *, keep_last: int, dry_run: bool = True) -> BenchmarkVersionPruneResponse:
        return self._store.prune_versions(keep_last=keep_last, dry_run=dry_run)

    def scan_version_health(self) -> BenchmarkVersionHealthResponse:
        return self._store.scan_version_health()

    def repair_versions(self, *, dry_run: bool = True) -> BenchmarkVersionRepairResponse:
        return self._store.repair_versions(dry_run=dry_run)

    def build_maintenance_report(self, *, limit: int = 50) -> BenchmarkMaintenanceReportResponse:
        return self._store.build_maintenance_report(limit=limit)

    def auto_remediate_versions(
        self,
        *,
        dry_run: bool = True,
        keep_last: int = 50,
    ) -> BenchmarkVersionAutoRemediateResponse:
        return self._store.auto_remediate_versions(dry_run=dry_run, keep_last=keep_last)

    def build_maintenance_alert(self, *, limit: int = 50) -> BenchmarkMaintenanceAlertResponse:
        return self._store.build_maintenance_alert(limit=limit)

    def emit_maintenance_alert(self, *, limit: int = 50) -> BenchmarkMaintenanceAlertEmitResponse:
        return self._store.emit_maintenance_alert(limit=limit)

    def list_maintenance_alerts(self, *, limit: int = 100, cursor: str = "") -> BenchmarkMaintenanceAlertListResponse:
        return self._store.list_maintenance_alerts(limit=limit, cursor=cursor)

    def prune_maintenance_alerts(
        self,
        *,
        keep_last: int,
        dry_run: bool = True,
    ) -> BenchmarkMaintenanceAlertPruneResponse:
        return self._store.prune_maintenance_alerts(keep_last=keep_last, dry_run=dry_run)

    def summarize_maintenance_alerts(self, *, limit: int = 200) -> BenchmarkMaintenanceAlertSummaryResponse:
        return self._store.summarize_maintenance_alerts(limit=limit)

    def archive_maintenance_alerts(
        self,
        *,
        keep_last: int,
        shard_size: int = 1000,
        dry_run: bool = True,
    ) -> BenchmarkMaintenanceAlertArchiveResponse:
        return self._store.archive_maintenance_alerts(keep_last=keep_last, shard_size=shard_size, dry_run=dry_run)

    def list_maintenance_alert_archive_files(self, *, limit: int = 200) -> BenchmarkMaintenanceAlertArchiveListResponse:
        return self._store.list_maintenance_alert_archive_files(limit=limit)

    def read_maintenance_alert_archive_file(
        self,
        *,
        file_name: str,
        limit: int = 100,
        cursor: str = "",
    ) -> BenchmarkMaintenanceAlertArchiveReadResponse:
        return self._store.read_maintenance_alert_archive_file(file_name=file_name, limit=limit, cursor=cursor)

    def auto_archive_maintenance_alerts(self, *, dry_run: bool = True) -> BenchmarkMaintenanceAlertAutoArchiveResponse:
        return self._store.auto_archive_maintenance_alerts(dry_run=dry_run)

    def cleanup_maintenance_alert_archives(self, *, dry_run: bool = True) -> BenchmarkMaintenanceAlertArchiveCleanupResponse:
        return self._store.cleanup_maintenance_alert_archives(dry_run=dry_run)

    def build_maintenance_alert_governance_report(
        self,
        *,
        alert_limit: int = 200,
        archive_limit: int = 200,
    ) -> BenchmarkMaintenanceAlertGovernanceReportResponse:
        return self._store.build_maintenance_alert_governance_report(alert_limit=alert_limit, archive_limit=archive_limit)

    def run_maintenance_alert_governance(
        self,
        *,
        dry_run: bool = True,
        alert_limit: int = 200,
        archive_limit: int = 200,
        idempotency_key: str = "",
        retry_run_id: str = "",
    ) -> BenchmarkMaintenanceAlertGovernanceRunResponse:
        return self._store.run_maintenance_alert_governance(
            dry_run=dry_run,
            alert_limit=alert_limit,
            archive_limit=archive_limit,
            idempotency_key=idempotency_key,
            retry_run_id=retry_run_id,
        )

    def list_maintenance_alert_governance_runs(
        self,
        *,
        limit: int = 100,
        cursor: str = "",
    ) -> BenchmarkMaintenanceAlertGovernanceRunListResponse:
        return self._store.list_maintenance_alert_governance_runs(limit=limit, cursor=cursor)

    def prune_maintenance_alert_governance_runs(
        self,
        *,
        keep_last: int,
        dry_run: bool = True,
    ) -> BenchmarkMaintenanceAlertGovernanceRunPruneResponse:
        return self._store.prune_maintenance_alert_governance_runs(keep_last=keep_last, dry_run=dry_run)

    def summarize_maintenance_alert_governance_runs(
        self,
        *,
        limit: int = 200,
    ) -> BenchmarkMaintenanceAlertGovernanceRunSummaryResponse:
        return self._store.summarize_maintenance_alert_governance_runs(limit=limit)

    def export_maintenance_alert_governance_runs(
        self,
        *,
        limit: int = 200,
        cursor: str = "",
    ) -> BenchmarkMaintenanceAlertGovernanceRunExportResponse:
        return self._store.export_maintenance_alert_governance_runs(limit=limit, cursor=cursor)

    def auto_prune_maintenance_alert_governance_runs(
        self,
        *,
        dry_run: bool = True,
    ) -> BenchmarkMaintenanceAlertGovernanceRunAutoPruneResponse:
        return self._store.auto_prune_maintenance_alert_governance_runs(dry_run=dry_run)

    def build_maintenance_alert_governance_runs_digest(
        self,
        *,
        limit: int = 200,
    ) -> BenchmarkMaintenanceAlertGovernanceRunDigestResponse:
        return self._store.build_maintenance_alert_governance_runs_digest(limit=limit)

    def emit_maintenance_alert_governance_escalation(
        self,
        *,
        limit: int = 200,
        ignore_cooldown: bool = False,
    ) -> BenchmarkMaintenanceAlertGovernanceEscalationEmitResponse:
        return self._store.emit_maintenance_alert_governance_escalation(
            limit=limit,
            ignore_cooldown=ignore_cooldown,
        )

    def list_maintenance_alert_governance_escalations(
        self,
        *,
        limit: int = 100,
        cursor: str = "",
    ) -> BenchmarkMaintenanceAlertGovernanceEscalationListResponse:
        return self._store.list_maintenance_alert_governance_escalations(limit=limit, cursor=cursor)

    def summarize_maintenance_alert_governance_escalations(
        self,
        *,
        limit: int = 200,
    ) -> BenchmarkMaintenanceAlertGovernanceEscalationSummaryResponse:
        return self._store.summarize_maintenance_alert_governance_escalations(limit=limit)

    def export_maintenance_alert_governance_escalations(
        self,
        *,
        limit: int = 200,
        cursor: str = "",
    ) -> BenchmarkMaintenanceAlertGovernanceEscalationExportResponse:
        return self._store.export_maintenance_alert_governance_escalations(limit=limit, cursor=cursor)

    def prune_maintenance_alert_governance_escalations(
        self,
        *,
        keep_last: int,
        dry_run: bool = True,
    ) -> BenchmarkMaintenanceAlertGovernanceEscalationPruneResponse:
        return self._store.prune_maintenance_alert_governance_escalations(keep_last=keep_last, dry_run=dry_run)

    def auto_prune_maintenance_alert_governance_escalations(
        self,
        *,
        dry_run: bool = True,
    ) -> BenchmarkMaintenanceAlertGovernanceEscalationAutoPruneResponse:
        return self._store.auto_prune_maintenance_alert_governance_escalations(dry_run=dry_run)

    def build_maintenance_alert_governance_escalations_digest(
        self,
        *,
        limit: int = 200,
    ) -> BenchmarkMaintenanceAlertGovernanceEscalationDigestResponse:
        return self._store.build_maintenance_alert_governance_escalations_digest(limit=limit)

    def auto_remediate_maintenance_alert_governance_escalations(
        self,
        *,
        dry_run: bool = True,
        limit: int = 200,
    ) -> BenchmarkMaintenanceAlertGovernanceEscalationAutoRemediateResponse:
        return self._store.auto_remediate_maintenance_alert_governance_escalations(dry_run=dry_run, limit=limit)

    def list_maintenance_alert_governance_escalation_remediations(
        self,
        *,
        limit: int = 100,
        cursor: str = "",
    ) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationListResponse:
        return self._store.list_maintenance_alert_governance_escalation_remediations(limit=limit, cursor=cursor)

    def summarize_maintenance_alert_governance_escalation_remediations(
        self,
        *,
        limit: int = 200,
    ) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationSummaryResponse:
        return self._store.summarize_maintenance_alert_governance_escalation_remediations(limit=limit)

    def export_maintenance_alert_governance_escalation_remediations(
        self,
        *,
        limit: int = 200,
        cursor: str = "",
    ) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationExportResponse:
        return self._store.export_maintenance_alert_governance_escalation_remediations(limit=limit, cursor=cursor)

    def prune_maintenance_alert_governance_escalation_remediations(
        self,
        *,
        keep_last: int,
        dry_run: bool = True,
    ) -> BenchmarkMaintenanceAlertGovernanceEscalationRemediationPruneResponse:
        return self._store.prune_maintenance_alert_governance_escalation_remediations(
            keep_last=keep_last,
            dry_run=dry_run,
        )

    def auto_remediate_maintenance_alert_governance_runs(
        self,
        *,
        dry_run: bool = True,
        limit: int = 200,
        alert_limit: int = 200,
        archive_limit: int = 200,
    ) -> BenchmarkMaintenanceAlertGovernanceRunAutoRemediateResponse:
        return self._store.auto_remediate_maintenance_alert_governance_runs(
            dry_run=dry_run,
            limit=limit,
            alert_limit=alert_limit,
            archive_limit=archive_limit,
        )

    def build_maintenance_alert_digest(self, *, limit: int = 200) -> BenchmarkMaintenanceAlertDigestResponse:
        return self._store.build_maintenance_alert_digest(limit=limit)

    def export_maintenance_alerts(self, *, limit: int = 200, cursor: str = "") -> BenchmarkMaintenanceAlertExportResponse:
        return self._store.export_maintenance_alerts(limit=limit, cursor=cursor)
