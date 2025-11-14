from .game import Game
from .board_sizes import SMALL_BOARD_SIZE


if __name__ == '__main__':
    board = Game(board_size=SMALL_BOARD_SIZE)
    board.play()
