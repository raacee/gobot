import numpy as np
from collections import deque
from copy import deepcopy
from .player import Human, Player
from .stones import (
    WHITE_STONE,
    BLACK_STONE,
    WHITE_STONE_CHAR,
    BLACK_STONE_CHAR,
    EMPTY,
    EMPTY_CHAR,
)


class Board:
    def __init__(self, board_size: int, super_ko: bool = False):
        self._board_size: int = board_size
        self._board = np.array(
            [[EMPTY] * self._board_size] * self._board_size
        )
        self._super_ko: bool = super_ko
        self._last_boards: set() = set()
        self._board.flags.writeable = False
        self._last_boards.add(self._board.data.tobytes())
        self._players: deque[Player] = deque(
            [Human(stone=BLACK_STONE), Human(stone=WHITE_STONE)]
        )
        self._captured_black_stones: int = 0

    def _is_case_occupied(self, x: int, y: int) -> bool:
        return self._board[x, y] != 0

    def _check_ko(self, board) -> bool:
        return board in self._last_board

    def _game_iteration(self):
        # Begin new player turn
        current_player: Player = self._players[0]
        print(self)
        print(f"Player {current_player.name}'s turn")
        print("Place a stone on a valid case")

        # Players chooses a stone
        x, y = current_player.choose_case(self._board)

        if x >= self._board_size or y >= self._board_size:
            print("Coordinates bigger than board_size")
            return

        # TODO: check for ko
        # TODO: At each turn, save turn and check if next turn leads to saved turn

        # Check if case is unoccupied
        if self._is_case_occupied(x, y):
            print("Case is occupied")
            return

        # Check if case induces suicide
        test_board = deepcopy(self._board)
        test_board[x, y] = current_player.stone

        neighbors = [(x_n, y_n) for x_n, y_n in Board._neighbors_indices(test_board, x, y)]
        same_stone_group_dicts = Board._flood_fill(x, y, test_board, border=True)

        opposite_stone = current_player.stone * -1
        opposite_stone_neighbors_coords = [(x_n, y_n) for x_n, y_n in neighbors if self._board[x_n, y_n] == opposite_stone]
        opposite_stone_neighbors_group_dicts = [Board._flood_fill(x_n, y_n, test_board, border=True) for x_n, y_n in opposite_stone_neighbors_coords]

        # Check in every border if a 0 is present
        for group_dict in opposite_stone_neighbors_group_dicts:
            Board._mark_capture(group_dict)

        induces_capture = len(list(filter(lambda d: d["captured"], opposite_stone_neighbors_group_dicts))) > 0
        induces_suicide = 0 not in same_stone_group_dicts["border"].values()

        if induces_suicide:
            if not induces_capture:
                print(
                    "Player case choice induces suicide with no capture, illegal move"
                )
                return

        if induces_capture:
            captured_groups = list(filter(lambda g:g["captured"], opposite_stone_neighbors_group_dicts))
            captured_groups_coords = map(lambda g:g["group"].keys(), captured_groups)
            captured_groups_coords = [t for coords in captured_groups_coords for t in coords]
            for coord in captured_groups_coords:
                test_board[coord] = 0 # Indexing doesn't work like this

        test_board.flags.writeable = False
        if self._super_ko:
            if test_board in self._last_boards:
                print("Super Ko is enabled and chosen case leads to previously reached board")
            else:
                self._last_boards.append(test_board.data.tobytes())
        else:
            self._last_boards = [deepcopy(test_board)]

        test_board.flags.writeable = True
        self._board = test_board
        self._players.rotate()

    def game(self):
        while True:
            self._game_iteration()

        # End of game, counting
        print("Game has ended")
        winner = self._winner()
        if winner == -1:
            print("Black player won !")
        else:
            print("White player won !")
        return

    @staticmethod
    def _flood_fill(x: int, y: int, board:np.typing.NDArray, border=True) -> set[tuple[int, int]]:
        """Algorithm to find groups of stones"""
        """Also counts the empty cases for liberty and capture checking"""
        """border default parameter allows to add border cases to res"""
        """Returns res, a dict of two dicts : one for the border and one for the group"""
        """The two dicts each have coordinate tuples as keys and stones as values"""
        """This allows calls to keys() to return the coordinates tuples and values() calls to return the stone values"""

        queue: deque[tuple[int]] = deque()
        queue.append((x, y))
        res:dict[str, set[tuple[int,int]]]={
            "group":dict(),
            "border":dict()
        }
        stone = board[x, y]

        while len(queue) > 0:
            x, y = queue.popleft()
            if (x, y) not in res["group"].keys() and (x,y) not in res["border"].keys():
                if board[x, y] == stone:
                    res["group"][(x, y)] = board[x, y]
                    neighbors = Board._neighbors_indices(board, x, y)
                    queue.extend(neighbors)
                else:
                    if border:
                        res["border"][(x, y)] = board[x, y]
        return res

    @staticmethod
    def _mark_capture(group_dict: dict[str,set[tuple[int,int]]]):
        if 0 not in group_dict["border"].values():
            group_dict["captured"] = True
        else:
            group_dict["captured"] = False

    @staticmethod
    def _neighbors_indices(board, x, y) -> set[tuple[int, int]]:
        board_size = board.shape[0]
        neighbors = []
        if x != 0:
            neighbors.append((x - 1, y))
        if x != board_size - 1:
            neighbors.append((x + 1, y))
        if y != 0:
            neighbors.append((x, y - 1))
        if y != board_size - 1:
            neighbors.append((x, y + 1))
        return set(neighbors)

    def _winner(self) -> int:
        board = self._board[::, ::]
        black_stones = (
            np.sum((board == BLACK_STONE).astype(int)) + self._captured_black_stones
        )
        return 1 if black_stones > (self._board_size**2) // 2 else -1

    def __str__(self) -> str:
        str_board = self._board[::, ::].astype(str)
        str_board[str_board == "1"] = BLACK_STONE_CHAR
        str_board[str_board == "-1"] = WHITE_STONE_CHAR
        str_board[str_board == "0"] = EMPTY_CHAR

        return str_board.__str__()
