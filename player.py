class Player:
    def __init__(self, stone: int) -> None:
        self.stone = stone

    def choose_case(self) -> tuple[int, ...]:
        return tuple(int(v) for v in input().split()[:2])
