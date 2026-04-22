from __future__ import annotations

from dataclasses import dataclass, field

from alpha_autopilot_v2.domain import RuleCheck, SearchResult, StoryState
from alpha_autopilot_v2.search.service import SearchService


@dataclass
class NarrativeV2SearchService:
    core: SearchService = field(default_factory=SearchService)

    def search(self, state: StoryState, checks: list[RuleCheck]) -> list[SearchResult]:
        return self.core.search(state, checks)
