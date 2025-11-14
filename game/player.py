from abc import ABC, abstractmethod
from collections import deque
from .stones import WHITE_STONE, BLACK_STONE, stone_names


class Player(ABC):
    def __init__(self, stone: int) -> None:
        if stone not in [WHITE_STONE, BLACK_STONE]:
            raise ValueError("Stone must be black (-1) or white (1)")
        self.stone: int = stone
        self.name = "White" if stone == WHITE_STONE else "Black"

    def __str__(self):
        return stone_names[self.stone].__str__()

    @abstractmethod
    def choose_case(self) -> tuple[int, int] | None:
        raise NotImplementedError()


class Human(Player):
    def choose_case(self) -> tuple[int, int] | None:
        choice = input("Enter your move (row and column): ").split()[:2]
        if choice == []:
            return None
        else:
            return tuple(
                int(v) for v in choice
            )
