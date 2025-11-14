from game.player import Player
from game.stones import stone_names
from collections import deque
from typing import override


class Bot(Player):
    def __init__(self, stone: int) -> None:
        super().__init__(stone)

    @override
    def choose_case(self, board=None) -> tuple[int, int] | None:
        return self._find_best_move(board)

    def _find_best_move(self, board) -> tuple[int, int] | None:
        raise NotImplementedError()


class ProgrammedBot(Bot):
    def __init__(self, stone: int, moves: list[tuple[int, int] | None]) -> None:
        super().__init__(stone)
        self._moves = deque(moves)

    @override
    def choose_case(self, board=None) -> tuple[int, int] | None:
        return self._moves.popleft()

    def n_moves_remaining(self):
        return len(self._moves)
