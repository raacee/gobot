import numpy as np


class Board():
    def __init__(self, board_size:int):
        self.board_size: int = board_size
        self.players: tuple[Player, Player] = (Player(1), Player(-1))
        self._current_player_index: int = 1
        self.current_player: Player = self.players[self._current_player_index]
        self.board: np.ndarray = np.array([[0] * self.board_size] * self.board_size)

    def _is_over(self) -> bool:
        return (self.board == 0).sum() == 0

    def _check_valid_case(self, x, y) -> bool:
        return self.board[x,y] == 0

    def game(self):
        mask = np.array(
            [
                [False, True, False],
                [True, False, True],
                [False, True, False]
            ]
        )

        while self._is_over() != False:
            print(f"Player {self.current_player}'s turn")
            print("Place a stone on a valid case")
            valid_case: bool = False
            while(valid_case == False):
                x, y = self.current_player.choose_case()
                valid_case = self._check_valid_case(x, y)
            self._current_player_index *= -1
            self.current_player = self.players[self._current_player_index]

            # Check captured stones
            adversary_near_stones = []
            np.ma.masked_where(mask, self.board)


        print("Game has ended")
        print(f"Player {self._current_player_index} won !")


    def _flood_fill(self, x, y):
        adversary = self.players[self._current_player_index * -1]

        return

    def _display(self):
        print(self.board)


class Player():
    def __init__(self, n):
        self.n = n

    def choose_case(self) -> tuple[int,...]:
        return tuple(int(v) for v in input().split())

if __name__ == '__main__':
    board = Board(board_size=19)
    board.game()
