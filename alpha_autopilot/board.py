from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple


Position = Tuple[int, int]


@dataclass(frozen=True)
class Move:
    src: Position
    dst: Position
    captured: Optional[str] = None


@dataclass
class BoardState:
    board: List[List[str]]
    current_player: str = "red"

    @classmethod
    def initial(cls) -> "BoardState":
        board = [["." for _ in range(9)] for _ in range(10)]
        board[0] = ["rR", "rH", "rE", "rA", "rK", "rA", "rE", "rH", "rR"]
        board[2][1] = "rC"
        board[2][7] = "rC"
        board[3][0] = board[3][2] = board[3][4] = board[3][6] = board[3][8] = "rP"
        board[9] = ["bR", "bH", "bE", "bA", "bK", "bA", "bE", "bH", "bR"]
        board[7][1] = "bC"
        board[7][7] = "bC"
        board[6][0] = board[6][2] = board[6][4] = board[6][6] = board[6][8] = "bP"
        return cls(board=board, current_player="red")

    def clone(self) -> "BoardState":
        return BoardState(board=[row[:] for row in self.board], current_player=self.current_player)

    def pieces(self):
        for r, row in enumerate(self.board):
            for c, piece in enumerate(row):
                if piece != ".":
                    yield r, c, piece

    def move_piece(self, move: Move) -> "BoardState":
        new_state = self.clone()
        sr, sc = move.src
        dr, dc = move.dst
        piece = new_state.board[sr][sc]
        new_state.board[sr][sc] = "."
        new_state.board[dr][dc] = piece
        new_state.current_player = "black" if self.current_player == "red" else "red"
        return new_state

    def inside(self, r: int, c: int) -> bool:
        return 0 <= r < 10 and 0 <= c < 9

    def color_of(self, piece: str) -> str:
        return "red" if piece.startswith("r") else "black"

    def enemy(self, piece: str) -> bool:
        return self.color_of(piece) != self.current_player
