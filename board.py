import numpy as np
from collections import deque
from player import Player
from pickle import TRUE


class Board:
    _mask = np.array(
        [
            [False, True, False],
            [True, False, True],
            [False, True, False]
        ]
    )

    BLACK_STONE=1
    WHITE_STONE=-1
    EMPTY=0

    def __init__(self, board_size:int):
        self._board_size: int = board_size
        self._board: np.ndarray = np.array([[Board.EMPTY] * self._board_size] * self._board_size)
        self._last_board: np.ndarray = np.array([[Board.EMPTY] * self._board_size] * self._board_size)
        self._players = deque([Player(stone=Board.BLACK_STONE), Player(stone=Board.WHITE_STONE)])
        self._last_turn_induced_capture = False


    def _is_over(self) -> bool:
        raise NotImplementedError

    def _check_case_occupied(self, x, y) -> bool:
        return self._board[x,y] == 0

    def _check_ko(self, x, y):
        return

    def game(self):
        while not self._is_over():
            current_player: Player = self._players[0]
            print(f"Player {current_player}'s turn")
            print("Place a stone on a valid case")

            # Players chooses a stone
            x, y = current_player.choose_case()

            # TODO: check for ko
            # At each turn, save turn and check if next turn leads to saved turn

            # Check if case is unoccupied
            if self._check_case_occupied(x, y):
                print("Case is occupied")
                continue


            # Check if case induces suicide
            self._board[x, y] = current_player.stone
            induces_suicide = self._induces_suicide(x, y, current_player.stone)
            if induces_suicide:
                print("Placing a stone here induces suicide. Forbidden move.")
                self._board[x, y] = Board.EMPTY
                continue

            # Check if case induces capture
            neighbors = self._neighbors_indices(x, y)
            # already_checked_stones_indices = set()
            for x_n, y_n in neighbors:
                neighbor_stone = self._board[x_n, y_n]
                if neighbor_stone == current_player.stone * -1:
                    group_indices_tuples = self._flood_fill(x_n, y_n, neighbor_stone)
                    group_stones = [0] * len(group_indices_tuples)
                    for i, index in enumerate(group_indices_tuples):
                        group_stones[i] = self._board[index]
                    if 0 not in group_stones:
                        print(f"Player {current_player.stone} captures group")
                        for i, index in enumerate(group_indices_tuples):
                            self._board[index] = 0
                        # already_checked_stones_indices.update(group_indices_tuples)

            self._players.rotate()
            np.ma.masked_where(Board._mask, self._board)

        print("Game has ended")
        print(f"Player {self._players[0]} won !")

    def _flood_fill(self, x: int, y: int, stone: int) -> set[tuple[int, int]]:
        """Algorithm to find groups of stones"""
        """Also counts the empty cases for liberty and capture checking"""
        queue = deque()
        queue.append((x, y))
        res = set()
        while len(queue) > 0:
            x, y = queue.popleft()
            if (x, y) not in res:
                if self._board[x, y] == Board.EMPTY:
                    res.add((x,y))
                    continue
                elif self._board[x, y] == stone:
                    res.add((x,y))
                    neighbors = self._neighbors_indices(x, y)
                    queue.extend(neighbors)
        return res

    def _flood_fill_rec(self, x: int, y: int, stone:int, res: set[tuple[int,int]] = set()) -> None:
        if self._board[x, y] != stone:
            res.add((x, y))
            neighbors = self._neighbors_indices(x, y)
            if neighbors & res == neighbors:
                return
            for x_n, y_n in neighbors:
                self._flood_fill_rec(x_n, y_n, stone, res)

    def _induces_suicide(self, x: int, y: int, stone: int) -> bool:
        """Same algorithm as flood fill, excepts it stops once it finds a 0"""
        queue = deque()
        queue.append((x, y))
        checked = set()
        while len(queue) > 0:
            x, y = queue.popleft()
            if (x, y) not in checked:
                if self._board[x, y] == Board.EMPTY:
                    checked.add((x,y))
                    return False
                elif self._board[x, y] == stone:
                    checked.add((x,y))
                    neighbors = self._neighbors_indices(x, y)
                    queue.extend(neighbors)
        return True

    def _neighbors_indices(self, x, y) -> set[tuple[int,int]]:
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

    def __repr__(self):
        return self._board.__repr__()
