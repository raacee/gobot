from abc import ABC, abstractmethod
from .stones import WHITE_STONE, BLACK_STONE

class Player(ABC):
    def __init__(self, stone: int) -> None:
        if stone not in [WHITE_STONE, BLACK_STONE]:
            raise ValueError("Stone must be black (-1) or white (1)")
        self.stone = stone

    @abstractmethod
    def choose_case(self, board=None) -> tuple[int, ...]:
        pass

class Human(Player):
    def choose_case(self, board=None) -> tuple[int, ...]:
        return tuple(int(v) for v in input("Enter your move (row and column): ").split()[:2])

class Bot(Player):
    def __init__(self, stone: int) -> None:
        super().__init__(stone)

    def choose_case(self, board=None) -> tuple[int, ...]:
        return self._find_best_move(board)

    def _find_best_move(self, board) -> tuple[int, ...]:
        raise NotImplementedError()
