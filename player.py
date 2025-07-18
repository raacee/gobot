import board


class Player:
    def __init__(self, stone: int) -> None:
        if stone not in [board.WHITE_STONE, board.BLACK_STONE]:
            raise ValueError("Stone must be black (-1) or white (1)")
        self.stone = stone

    def choose_case(self) -> tuple[int, ...]:
        return tuple(int(v) for v in input().split()[:2])
