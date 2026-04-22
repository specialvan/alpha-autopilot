from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from alpha_autopilot_v2.validation.ledger import append_ledger_entry, read_ledger_entries
from alpha_autopilot_v2.validation.models import EvaluationLedgerEntry, ValidationRecord


@dataclass
class NarrativeV2ValidationService:
    def record(
        self,
        case_id: str,
        accepted_actions: list[str],
        blocked_actions: list[str],
        top_action: str,
        notes: str = "",
    ) -> ValidationRecord:
        return ValidationRecord(
            case_id=case_id,
            accepted_actions=accepted_actions,
            blocked_actions=blocked_actions,
            top_action=top_action,
            notes=notes,
        )

    def append_ledger(
        self,
        record: ValidationRecord,
        source: str = "manual",
        path: Path | None = None,
    ) -> EvaluationLedgerEntry:
        entry = EvaluationLedgerEntry(
            case_id=record.case_id,
            top_action=record.top_action,
            accepted_actions=list(record.accepted_actions),
            blocked_actions=list(record.blocked_actions),
            notes=record.notes,
            source=source,
            recorded_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        )
        append_ledger_entry(entry, path=path)
        return entry

    def read_ledger(self, path: Path | None = None) -> list[EvaluationLedgerEntry]:
        return read_ledger_entries(path=path)
