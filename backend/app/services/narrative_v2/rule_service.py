from __future__ import annotations

from dataclasses import dataclass, field

from alpha_autopilot_v2.domain import RuleCheck, StoryState
from alpha_autopilot_v2.rules.service import RuleService


@dataclass
class NarrativeV2RuleService:
    core: RuleService = field(default_factory=RuleService)

    def evaluate(self, state: StoryState) -> list[RuleCheck]:
        return self.core.evaluate(state)
