import numpy as np
from collections import deque


class Board():
    _mask = np.array(
        [
            [False, True, False],
            [True, False, True],
            [False, True, False]
        ]
    )

    def __init__(self, board_size:int):
        self._board_size: int = board_size
        self._players: tuple[Player, Player] = (Player(1), Player(-1))
        self._current_player_index: int = 1
        self._current_player: Player = self._players[self._current_player_index]
        self._board: np.ndarray = np.array([[0] * self._board_size] * self._board_size)

    def _is_over(self) -> bool:
        return (self._board == 0).sum() == 0

    def _check_valid_case(self, x, y) -> bool:
        return self._board[x,y] == 0

    def game(self):
        while self._is_over() != False:
            print(f"Player {self.current_player}'s turn")
            print("Place a stone on a valid case")
            valid_case: bool = False
            while(valid_case == False):
                x, y = self.current_player.choose_case()
                valid_case = self._check_valid_case(x, y)
            self._current_player_index *= -1
            self.current_player = self._players[self._current_player_index]

            # Check captured stones
            adversary_near_stones = []
            np.ma.masked_where(Board._mask, self._board)

        print("Game has ended")
        print(f"Player {self._current_player_index} won !")

    def _flood_fill(self, x: int, y: int, res: set = set()) -> set[tuple[int, int]]:
        # if all neighbors in res, return res


        if self._board[x, y] == self._players[self._current_player_index * -1]:
            res.add((x,y))
            if x != 0:
                self._flood_fill(x-1, y, res)
            if x != self._board_size - 1:
                self._flood_fill(x+1, y, res)
            if y != 0:
                self._flood_fill(x, y-1, res)
            if y != self._board_size - 1:
                self._flood_fill(x, y+1, res)
        else:
            res.add(None)

    def _neighbors(self, x, y):
        neighbors = []
        if x != 0:
            neighbors.append((x-1, y))
        if x != self._board_size - 1:
            neighbors.append((x+1, y))
        if y != 0:
            neighbors.append((x, y-1))
        if y != self._board_size - 1:
            neighbors.append((x, y+1))

    def _display(self):
        print(self._board)


class Player():
    def __init__(self, n):
        self.n = n

    def choose_case(self) -> tuple[int, ...]:
        return tuple(int(v) for v in input().split()[:2])

if __name__ == '__main__':
    board = Board(board_size=19)
    board.game()
