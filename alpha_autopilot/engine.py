from __future__ import annotations

from typing import Optional, Tuple

from .board import BoardState, Move
from .eval import FeatureEvaluator
from .search import AlphaBetaSearch


class AlphaAutopilotEngine:
    def __init__(self) -> None:
        self.evaluator = FeatureEvaluator()
        self.search = AlphaBetaSearch(self.evaluator)

    def initial_state(self) -> BoardState:
        return BoardState.initial()

    def best_move(self, state: BoardState) -> Tuple[Optional[Move], int]:
        return self.search.best_move(state)
