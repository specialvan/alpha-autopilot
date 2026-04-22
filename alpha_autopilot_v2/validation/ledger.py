from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .assets import ledger_dir
from .models import EvaluationLedgerEntry


def default_ledger_path() -> Path:
    return ledger_dir() / "evaluation-ledger.jsonl"


def append_ledger_entry(entry: EvaluationLedgerEntry, path: Path | None = None) -> Path:
    ledger_path = path or default_ledger_path()
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with ledger_path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(asdict(entry), ensure_ascii=True))
        handle.write("\n")
    return ledger_path


def read_ledger_entries(path: Path | None = None) -> list[EvaluationLedgerEntry]:
    ledger_path = path or default_ledger_path()
    if not ledger_path.exists():
        return []
    entries: list[EvaluationLedgerEntry] = []
    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        entries.append(EvaluationLedgerEntry(**payload))
    return entries
