import numpy as np
from collections import deque
from player import Player


class Board:
    BLACK_STONE=1
    WHITE_STONE=-1
    PASS = []
    EMPTY=0

    def __init__(self, board_size:int, super_ko:bool = False):
        self._board_size: int = board_size
        self._board: np.ndarray = np.array([[Board.EMPTY] * self._board_size] * self._board_size)
        self._super_ko: bool = super_ko
        if self._super_ko:
            self._last_boards = [
                self._board[::,::]
            ]
        else:
            self._last_boards = (
                self._board[::,::]
                ,
            )
        self._players: deque[Player] = deque([Player(stone=Board.BLACK_STONE), Player(stone=Board.WHITE_STONE)])
        self._last_turn_induced_capture: bool = False
        self._captured_black_stones: int = 0

    def _is_case_occupied(self, x, y) -> bool:
        return self._board[x,y] != 0

    def _check_ko(self, x, y, board) -> bool:
        if self._super_ko:
            return board in self._last_boards
        else:
            return board == self._last_boards[0]

    def game(self):
        last_turned_passed = False
        while True:
            # Begin new player turn
            current_player: Player = self._players[0]
            print(f"Player {current_player}'s turn")
            print("Place a stone on a valid case")

            # Players chooses a stone
            player_choice = current_player.choose_case()
            # Check if player has chosen to pass
            if player_choice == Board.PASS:
                # If player chose to pass check if last turned was passed
                if last_turned_passed:
                    # If it did, break and initiate counting
                    break
                else:
                    # Else, set flag to True and skip turn
                    last_turned_passed = True
                    self._players.rotate()
                    continue
            else:
                last_turned_passed = False

            x, y = player_choice

            # TODO: check for ko
            # At each turn, save turn and check if next turn leads to saved turn

            # Check if case is unoccupied
            if self._is_case_occupied(x, y):
                print("Case is occupied")
                continue

            # Check if case induces suicide
            test_board = self._board[::,::]
            self._board[x, y] = current_player.stone
            induces_suicide = self._induces_suicide(x, y, current_player.stone, test_board)
            if induces_suicide:
                print("Placing a stone here induces suicide. Forbidden move.")
                self._board[x, y] = Board.EMPTY
                continue
            else:
                self._board = test_board

            # Check if case induces capture
            neighbors = self._neighbors_indices(x, y)
            # already_checked_stones_indices = set()
            for x_n, y_n in neighbors:
                neighbor_stone = self._board[x_n, y_n]
                if neighbor_stone == current_player.stone * -1:
                    group_indices_tuples = self._flood_fill(x_n, y_n, neighbor_stone)
                    n_stones = len(group_indices_tuples)
                    group_stones = [0] * n_stones
                    for i, index in enumerate(group_indices_tuples):
                        group_stones[i] = self._board[index]
                    if 0 not in group_stones:
                        print(f"Player {current_player.stone} captures group")
                        if neighbor_stone == Board.BLACK_STONE:
                            self._captured_black_stones += n_stones
                        for i, index in enumerate(group_indices_tuples):
                            self._board[index] = 0
                        # already_checked_stones_indices.update(group_indices_tuples)

            self._players.rotate()

        print("Game has ended")
        winner = self._winner()
        if winner == -1:
            print("Black player won !")
        else:
            print("White player won !")
        return

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

    def _induces_suicide(self, x: int, y: int, stone: int, board_array: np.ndarray) -> bool:
        """Same algorithm as flood fill, excepts it stops once it finds a 0"""
        queue = deque()
        queue.append((x, y))
        checked = set()
        while len(queue) > 0:
            x, y = queue.popleft()
            if (x, y) not in checked:
                if board_array[x, y] == Board.EMPTY:
                    checked.add((x,y))
                    return False
                elif board_array[x, y] == stone:
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

    def _winner(self) -> int:
        board = self._board[::,::]
        black_stones = np.sum((board == Board.BLACK_STONE).astype(int)) + self._captured_black_stones
        return -1 if black_stones > 180 else 1

    def __repr__(self):
        return self._board.__repr__()
