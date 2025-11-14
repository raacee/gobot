import unittest
from bot.loading import load_game_moves, find_game_files
from bot.bot import ProgrammedBot
from game import Game
from game.stones import BLACK_STONE, WHITE_STONE, EMPTY, PASS
from game.board_sizes import SMALL_BOARD_SIZE
import numpy as np
from game.signals import InducesSuicide, DoublePass, BreakingKo


class TestGames(unittest.TestCase):
    # Add this helper function to test_games.py
    def create_test_board(self, board_array, black_moves, white_moves):
        players = [
            ProgrammedBot(BLACK_STONE, black_moves),
            ProgrammedBot(WHITE_STONE, white_moves)
        ]
        return Game.new_board_from_array(board_array, players, display=False)

    # Add these test cases to test_games.py
    def test_pass(self):
        # Create a board with no stones
        board_array = np.zeros(SMALL_BOARD_SIZE)
        # Both players pass
        black_moves = [PASS]
        white_moves = [PASS]
        game = self.create_test_board(board_array, black_moves, white_moves)
        initial_board = game.get_board()
        # Both players pass without errors
        game._game_iteration()
        next_board = game.get_board()
        self.assertTrue(np.all(initial_board == next_board))
        with self.assertRaises(DoublePass):
            game._game_iteration()
            final_board = game.get_board()
            self.assertEqual(initial_board, next_board)

    def test_move(self):
        # Create a board with no stones
        board_array = np.zeros(SMALL_BOARD_SIZE)
        # Black plays at (0, 0), White plays at (1, 1)
        black_moves = [(0, 0), None]
        white_moves = [(1, 1), None]
        board = self.create_test_board(board_array, black_moves, white_moves)
        # Both players make moves without errors
        board._game_iteration()
        board._game_iteration()
        self.assertEqual(board._board[0, 0], BLACK_STONE)
        self.assertEqual(board._board[1, 1], WHITE_STONE)

    def test_capture(self):
        # Create a board with a white stone at (1, 1) surrounded by black stones
        board_array = np.zeros(SMALL_BOARD_SIZE)
        board_array[0, 1] = BLACK_STONE
        board_array[1, 0] = BLACK_STONE
        board_array[1, 2] = BLACK_STONE
        board_array[2, 1] = BLACK_STONE
        # Black plays at (1, 1) to capture the white stone
        black_moves = [(1, 1), None]
        white_moves = [None, None]
        board = self.create_test_board(board_array, black_moves, white_moves)
        # Black captures the white stone without errors
        board._game_iteration()
        self.assertEqual(board._board[1, 1], BLACK_STONE)

    def test_suicide(self):
        # Create a board with black stones at (0, 0) and (0, 1)
        board_array = np.zeros(SMALL_BOARD_SIZE)
        board_array[0, 1] = BLACK_STONE
        board_array[8, 8] = WHITE_STONE
        # White tries to play at (0, 2), which is suicide
        black_moves = [(1,0)]
        white_moves = [(0, 0)]
        game = self.create_test_board(board_array, black_moves, white_moves)
        # White's move should raise an InducesSuicide exception
        with self.assertRaises(InducesSuicide):
            game._game_iteration()
            game._game_iteration()

    def test_suicide_capture(self):
        # Create a board with a white stone at (1, 1) and black stones at (0, 1) and (2, 1)
        board_array = np.zeros(SMALL_BOARD_SIZE)

        # White plays at (1, 0) to capture the white stone and commit suicide
        black_moves = [(0, 1), (1, 0), (1, 2)]
        white_moves = [(1, 1), (0, 2), (0, 0)]
        board = self.create_test_board(board_array, black_moves, white_moves)
        # Black's move should capture the white stone without errors
        for _ in range(0, 6):
            board._game_iteration()
        self.assertEqual(board._board[0, 1], EMPTY)

    def test_ko_rule(self):
        # Create a board with a white stone at (1, 1) and black stones at (0, 1) and (2, 1)
        board_array = np.zeros(SMALL_BOARD_SIZE)

        # White plays at (1, 0) to capture the white stone and commit suicide
        black_moves = [(0, 1), (1, 0), (1, 2), (0, 1)]
        white_moves = [(1, 1), (0, 2), (0, 0)]
        board = self.create_test_board(board_array, black_moves, white_moves)
        # Black's move should capture the white stone without errors
        with self.assertRaises(BreakingKo):
            for _ in range(0, 7):
                board._game_iteration()
