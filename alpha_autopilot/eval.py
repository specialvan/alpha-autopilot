from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .board import BoardState


PIECE_VALUE: Dict[str, int] = {
    "K": 1000000,
    "A": 110,
    "E": 110,
    "H": 300,
    "R": 600,
    "C": 300,
    "P": 70,
}

POSITION_TABLES: Dict[str, List[List[int]]] = {
    "H": [
        [0, 4, 8, 12, 16, 12, 8, 4, 0],
        [4, 8, 12, 16, 20, 16, 12, 8, 4],
        [8, 12, 16, 20, 24, 20, 16, 12, 8],
        [12, 16, 20, 24, 28, 24, 20, 16, 12],
        [16, 20, 24, 28, 32, 28, 24, 20, 16],
        [12, 16, 20, 24, 28, 24, 20, 16, 12],
        [8, 12, 16, 20, 24, 20, 16, 12, 8],
        [4, 8, 12, 16, 20, 16, 12, 8, 4],
        [0, 4, 8, 12, 16, 12, 8, 4, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
    ],
    "R": [[i + j for j in range(9)] for i in range(10)],
    "C": [[(4 - abs(4 - j)) * 2 for j in range(9)] for _ in range(10)],
    "P": [[(9 - i) * 3 for j in range(9)] for i in range(10)],
}


@dataclass
class FeatureEvaluator:
    def evaluate(self, state: BoardState) -> int:
        score = 0
        for r, c, piece in state.pieces():
            color = 1 if piece.startswith("r") else -1
            kind = piece[1]
            base = PIECE_VALUE.get(kind, 0)
            positional = POSITION_TABLES.get(kind, [[0] * 9 for _ in range(10)])[r][c] * 8
            score += color * (base + positional)
        return score if state.current_player == "red" else -score
