import numpy as np
from typing import Generator
from collections import deque
from copy import deepcopy
from .player import Human, Player
from .signals import *
from .stones import (
    WHITE_NAME,
    WHITE_STONE,
    BLACK_STONE,
    WHITE_STONE_CHAR,
    BLACK_STONE_CHAR,
    EMPTY,
    EMPTY_CHAR,
)


class Game:
    def __init__(self, board_size: tuple[int,int], players=None, super_ko: bool = False, display: bool = True, komi=7.5):
        self._board_size = board_size
        self._board = np.zeros(self._board_size).astype(int)
        self._super_ko: bool = super_ko
        self._last_boards: set[bytes] = set()
        if players is None:
            players = [Human(stone=BLACK_STONE), Human(stone=WHITE_STONE)]
        self._players: deque[Player] = deque(
            players
        )
        self._display: bool = display
        self._last_turned_passed: bool = False
        self._komi = komi

    @classmethod
    def new_board_from_array(cls, board, players, **kwargs):
        game = cls(board.shape, players, **kwargs)
        game._board = board
        return game

    def get_board(self):
        return self._board

    def get_current_player(self):
        return self._players[0]

    def _is_case_occupied(self, x: int, y: int) -> bool:
        return self._board[x, y] != 0

    def _check_ko(self, board:bytes) -> bool:
        return board in self._last_boards

    def _game_iteration(self) -> None:
        # Begin new player turn
        current_player: Player = self._players[0]
        if self._display:
            print(self)
            print(f"Player {current_player.name}'s turn")
            print("Place a stone on a valid case")

        player_choice = current_player.choose_case()

        # Players chooses a stone
        if player_choice is None:
            # If player chose to pass check if last turned was passed
            if self._last_turned_passed:
                # If it did, break and initiate counting
                raise DoublePass("Players both chose to pass, game over")
            else:
                # Else, set flag to True and skip turn
                self._last_turned_passed = True
                self._players.rotate()
                return
        else:
            self._last_turned_passed = False

        x, y = player_choice

        if x >= self._board_size[0] or y >= self._board_size[1]:
            raise IndexError("Coordinates bigger than board_size")

        # Check if case is unoccupied
        if self._is_case_occupied(x, y):
            raise OccupiedCase("Case is occupied")

        # Check if case induces suicide
        test_board = deepcopy(self._board)
        test_board[x, y] = current_player.stone

        neighbors = [(x_n, y_n) for x_n, y_n in Game._neighbors_indices(test_board, x, y)]
        same_stone_group_dicts = Game._flood_fill(x, y, test_board, border=True)

        opposite_stone = current_player.stone * -1
        opposite_stone_neighbors_coords = [(x_n, y_n) for x_n, y_n in neighbors if self._board[x_n, y_n] == opposite_stone]
        opposite_stone_neighbors_group_dicts = [Game._flood_fill(x_n, y_n, test_board, border=True) for x_n, y_n in opposite_stone_neighbors_coords]

        # Check in every border if a 0 is present
        for group_dict in opposite_stone_neighbors_group_dicts:
            Game._mark_capture(group_dict)

        induces_capture = len(list(filter(lambda d: d["captured"], opposite_stone_neighbors_group_dicts))) > 0
        induces_suicide = 0 not in same_stone_group_dicts["border"].values()

        if induces_suicide:
            if not induces_capture:
                raise InducesSuicide("Player case choice induces suicide with no capture, illegal move")

        if induces_capture:
            captured_groups = list(filter(lambda g:g["captured"], opposite_stone_neighbors_group_dicts))
            captured_groups_coords = map(lambda g:g["group"].keys(), captured_groups)
            captured_groups_coords = [t for coords in captured_groups_coords for t in coords]
            for coord in captured_groups_coords:
                test_board[coord] = 0 # Indexing doesn't work like this

        # Check for ko with test_board
        test_board.flags.writeable = False

        if test_board.data.tobytes() in self._last_boards:
            if self._super_ko:
                raise BreakingSuperKo("Super Ko is enabled and chosen case leads to previously reached board")
            else:
                raise BreakingKo("Breaking ko rule : chosen case leads to previously board")
        else:
            self._last_boards.add(test_board.data.tobytes())

        test_board.flags.writeable = True
        self._board = test_board
        self._players.rotate()

    def play(self):
        while True:
            try:
                self._game_iteration()
            except InvalidMove as ime:
                print(ime)
                continue
            except GameOver as goe:
                print(goe)
                break
            except IndexError as ie:
                print(f"Ended moves for player {self.get_current_player()}")
                break

        # End of game, initiate counting
        print("Game has ended")
        winner = self._winner()
        if winner == -1:
            if self._display:
                print("Black player won !")
            return "b"
        else:
            if self._display:
                print("White player won !")
            return "w"


    @staticmethod
    def _flood_fill(x: int, y: int, board:np.typing.NDArray, border=True) -> dict[str, dict[tuple[int, int], int]]:
        """Algorithm to find groups of stones"""
        """Also counts the empty cases for liberty and capture checking"""
        """border default parameter allows to add border cases to res"""
        """Returns res, a dict of two dicts : one for the border and one for the group"""
        """The two dicts each have coordinate tuples as keys and stones as values"""
        """This allows calls to keys() to return the coordinates tuples and values() calls to return the stone values"""

        queue: deque[tuple[int, int]] = deque()
        queue.append((x, y))
        res:dict[str, dict[tuple[int, int], int]] = {
            "group":dict(),
            "border":dict()
        }
        stone = board[x, y]

        # Might wanna use multiprocessing here, needs to use a multiprocessing.Queue instead of a deque
        while len(queue) > 0:
            x, y = queue.popleft()
            if (x, y) not in res["group"].keys() and (x, y) not in res["border"].keys():
                if board[x, y] == stone:
                    res["group"][(x, y)] = board[x, y]
                    neighbors = Game._neighbors_indices(board, x, y)
                    queue.extend(neighbors)
                else:
                    if border:
                        res["border"][(x, y)] = board[x, y]
        return res

    @staticmethod
    def _mark_capture(group_dict: dict[str, dict[tuple[int, int], int]]) :
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

    def _number_stones(self, stone: int):
        all_coordinates = self._all_tuples()
        return float(sum([1 for x, y in all_coordinates if self._board[x, y] == stone]))

    def _calculate_scores(self) -> dict[int, float]:
        all_coordinates = self._all_tuples()
        scores = {
            WHITE_STONE:self._number_stones(WHITE_STONE),
            BLACK_STONE:self._number_stones(BLACK_STONE)
        }
        checked = set()
        for x, y in all_coordinates:
            if self._board[x, y] == EMPTY and (x, y) not in checked:
                group_dict = Game._flood_fill(x, y, self._board)
                border = group_dict["border"].values()
                empty_spaces = group_dict["group"].values()
                if all(map(lambda stone:stone == BLACK_STONE, border)):
                    scores[BLACK_STONE] += len(empty_spaces)
                if all(map(lambda stone:stone == WHITE_STONE, border)):
                    scores[WHITE_STONE] += len(empty_spaces)
                group_coords = group_dict["group"].keys()
                checked.update(group_coords)

        scores[WHITE_STONE] += self._komi
        return scores

    def _winner(self):
        scores = self._calculate_scores()
        if scores[WHITE_STONE] > scores[BLACK_STONE]:
            return "w"
        elif scores[BLACK_STONE] > scores[WHITE_STONE]:
            return "b"
        else:
            return None

    def _all_tuples(self) -> Generator[tuple[int,int]]:
        for i in range(0, self._board_size[0]):
            for j in range(0, self._board_size[1]):
                yield (i, j)

    def __str__(self) -> str:
        str_board = self._board[::, ::].astype(str)
        str_board[str_board == "1"] = BLACK_STONE_CHAR
        str_board[str_board == "-1"] = WHITE_STONE_CHAR
        str_board[str_board == "0"] = EMPTY_CHAR

        return str_board.__str__()
