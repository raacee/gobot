import numpy as np
from collections import deque


class Board:
    _mask = np.array(
        [
            [False, True, False],
            [True, False, True],
            [False, True, False]
        ]
    )

    def __init__(self, board_size:int):
        self._board_size: int = board_size
        self._board: np.ndarray = np.array([[0] * self._board_size] * self._board_size)
        self._current_player = 1

    def _is_over(self) -> bool:
        return np.sum((self._board == 0)) == 0

    def _check_valid_case(self, x, y) -> bool:
        return self._board[x,y] == 0

    def game(self):
        while not self._is_over():
            print(f"Player {self._current_player}'s turn")
            print("Place a stone on a valid case")
            x, y = Board.choose_case()
            # Check if case induces suicide
            neighbors = self._neighbors(x, y)
            suicide = all(map(lambda x: x != self._current_player, neighbors))
            if suicide:
                print("Chosen case is not valid, induces suicide")

            # Check if case induces capture
            for x_n, y_n in neighbors:
                group_indices_tuples = self._flood_fill(x_n, y_n)
                group = np.zeros(len(group_indices_tuples))
                for t in group_indices_tuples:
                    group.append(self._board[np.array(t)])
                if 0 not in self._board[group]:
                    group


            for x_n, y_n in neighbors:
                if self._board[x_n, y_n] == self._current_player:
                    raise NotImplementedError
            self._current_player *= -1

            np.ma.masked_where(Board._mask, self._board)

        print("Game has ended")
        print(f"Player {self._current_player} won !")

    def _flood_fill(self, x: int, y: int) -> set[tuple[int, int]] | None:
        queue = deque()
        queue.append((x, y))
        res = set()

        while len(queue) > 0:
            x, y = queue.popleft()
            neighbors = self._neighbors(x, y)
            if self._board[x, y] != self._current_player:
                res.add((x,y))
                queue.extend(neighbors)
        return res

    def _flood_fill_rec(self, x: int, y: int, res: set[tuple[int,int]]) -> None:
        if self._board[x, y] != self._current_player:
            res.add((x, y))
            neighbors = self._neighbors(x, y)
            if neighbors & res == neighbors:
                return
            for x_n, y_n in neighbors:
                self._flood_fill_rec(x_n, y_n, res)

    def _neighbors(self, x, y) -> set[tuple[int,int]]:
        neighbors = []
        if x != 0:
            neighbors.append((x-1, y))
        if x != self._board_size - 1:
            neighbors.append((x+1, y))
        if y != 0:
            neighbors.append((x, y-1))
        if y != self._board_size - 1:
            neighbors.append((x, y+1))

        return set(neighbors)

    def _display(self):
        print(self._board)

    @staticmethod
    def choose_case() -> tuple[int, ...]:
        return tuple(int(v) for v in input().split()[:2])

if __name__ == '__main__':
    board = Board(board_size=19)
    board.game()
