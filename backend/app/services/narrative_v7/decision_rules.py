from __future__ import annotations

import json
import os
from pathlib import Path
from threading import RLock


_DEFAULT_RULES = {
    "early_chapter_limit": 3,
    "opening_t8_gate": 0.60,
    "tail_hook_zero_threshold": 0.01,
    "antagonist_drop_threshold": -0.20,
    "a6_sigma_lower": -2.0,
    "w6_floor": 0.40,
    "elastic_breakout_margin": 0.02,
}


class DecisionRuleSet:
    def __init__(self, *, config_path: str | None = None) -> None:
        self._lock = RLock()
        if config_path:
            self._config_path = Path(config_path)
        else:
            env_path = os.getenv("AA_V7_DECISION_RULES_JSON", "").strip()
            self._config_path = Path(env_path) if env_path else self._default_path()
        self._cached_rules = dict(_DEFAULT_RULES)
        self._cached_mtime_ns: int | None = None
        self._load_if_needed(force=True)

    def current(self) -> dict[str, float]:
        with self._lock:
            self._load_if_needed(force=False)
            return dict(self._cached_rules)

    def source_path(self) -> str:
        return str(self._config_path)

    def _load_if_needed(self, *, force: bool) -> None:
        if not self._config_path.exists():
            self._cached_rules = dict(_DEFAULT_RULES)
            self._cached_mtime_ns = None
            return

        stat = self._config_path.stat()
        mtime_ns = int(stat.st_mtime_ns)
        if not force and self._cached_mtime_ns == mtime_ns:
            return

        loaded = self._safe_load_rules(self._config_path)
        merged = dict(_DEFAULT_RULES)
        merged.update(loaded)
        self._cached_rules = merged
        self._cached_mtime_ns = mtime_ns

    def _safe_load_rules(self, path: Path) -> dict[str, float]:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}
        if not isinstance(payload, dict):
            return {}

        allowed_keys = set(_DEFAULT_RULES)
        output: dict[str, float] = {}
        for key, value in payload.items():
            if key not in allowed_keys:
                continue
            if isinstance(value, (int, float)):
                output[key] = float(value)
        return output

    def _default_path(self) -> Path:
        return Path(__file__).resolve().with_name("decision_rules.default.json")
