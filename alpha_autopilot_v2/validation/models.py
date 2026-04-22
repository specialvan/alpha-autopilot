from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ValidationRecord:
    case_id: str
    accepted_actions: list[str] = field(default_factory=list)
    blocked_actions: list[str] = field(default_factory=list)
    top_action: str = ""
    notes: str = ""


@dataclass
class EvaluationLedgerEntry:
    case_id: str
    top_action: str
    accepted_actions: list[str] = field(default_factory=list)
    blocked_actions: list[str] = field(default_factory=list)
    notes: str = ""
    source: str = "manual"
    recorded_at: str = ""
