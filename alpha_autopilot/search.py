from __future__ import annotations

from dataclasses import dataclass
from math import inf
from typing import Optional, Tuple

from .board import BoardState, Move
from .eval import FeatureEvaluator


@dataclass
class AlphaBetaSearch:
    evaluator: FeatureEvaluator
    max_depth: int = 4

    def adaptive_depth(self, state: BoardState) -> int:
        pieces = sum(1 for _ in state.pieces())
        if pieces > 24:
            return min(self.max_depth, 2)
        if pieces > 16:
            return min(self.max_depth, 4)
        return min(self.max_depth, 6)

    def best_move(self, state: BoardState) -> Tuple[Optional[Move], int]:
        depth = self.adaptive_depth(state)
        best_score = -inf
        best_move = None
        for move in self.generate_moves(state):
            score = -self.alphabeta(state.move_piece(move), depth - 1, -inf, inf)
            if score > best_score:
                best_score = score
                best_move = move
        return best_move, int(best_score if best_score != -inf else 0)

    def alphabeta(self, state: BoardState, depth: int, alpha: float, beta: float) -> float:
        if depth <= 0:
            return self.evaluator.evaluate(state)
        moves = self.generate_moves(state)
        if not moves:
            return self.evaluator.evaluate(state)
        value = -inf
        for move in moves:
            value = max(value, -self.alphabeta(state.move_piece(move), depth - 1, -beta, -alpha))
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return value

    def generate_moves(self, state: BoardState):
        moves = []
        for r, c, piece in state.pieces():
            if state.color_of(piece) != state.current_player:
                continue
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if not state.inside(nr, nc):
                    continue
                target = state.board[nr][nc]
                if target == "." or state.color_of(target) != state.current_player:
                    moves.append(Move((r, c), (nr, nc), None if target == "." else target))
        return moves
