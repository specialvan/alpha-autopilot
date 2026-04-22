from __future__ import annotations

from alpha_autopilot_v2.validation.ledger import (
    append_ledger_entry,
    default_ledger_path,
    read_ledger_entries,
)
from alpha_autopilot_v2.validation.models import EvaluationLedgerEntry, ValidationRecord
from backend.app.services.narrative_v2.validation_service import NarrativeV2ValidationService


def test_v2_core_ledger_appends_and_reads_jsonl_entries(tmp_path) -> None:
    ledger_path = tmp_path / "evaluation-ledger.jsonl"
    entry = EvaluationLedgerEntry(
        case_id="case-001",
        top_action="push_conflict",
        accepted_actions=["push_conflict"],
        blocked_actions=["deliver_payoff"],
        notes="baseline",
        source="test",
        recorded_at="2026-04-21T10:00:00Z",
    )

    append_ledger_entry(entry, path=ledger_path)
    append_ledger_entry(
        EvaluationLedgerEntry(
            case_id="case-002",
            top_action="deliver_payoff",
            accepted_actions=["deliver_payoff"],
            blocked_actions=["open_new_thread"],
            notes="late stage",
            source="test",
            recorded_at="2026-04-21T10:05:00Z",
        ),
        path=ledger_path,
    )
    entries = read_ledger_entries(path=ledger_path)

    assert len(entries) == 2
    assert entries[0].case_id == "case-001"
    assert entries[1].top_action == "deliver_payoff"
    assert default_ledger_path().name == "evaluation-ledger.jsonl"


def test_v2_validation_service_wraps_ledger_io(tmp_path) -> None:
    service = NarrativeV2ValidationService()
    record = ValidationRecord(
        case_id="case-003",
        accepted_actions=["reveal_clue"],
        blocked_actions=["deliver_payoff"],
        top_action="reveal_clue",
        notes="service wrapper",
    )

    entry = service.append_ledger(record, source="preview", path=tmp_path / "service-ledger.jsonl")
    entries = service.read_ledger(path=tmp_path / "service-ledger.jsonl")

    assert entry.source == "preview"
    assert entries[0].case_id == "case-003"
    assert entries[0].accepted_actions == ["reveal_clue"]
