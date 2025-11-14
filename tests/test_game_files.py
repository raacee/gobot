import unittest
from bot.loading import load_game_moves, find_game_files
from bot.bot import ProgrammedBot
from game import Game
from game.stones import BLACK_STONE, WHITE_STONE, EMPTY, PASS
from game.board_sizes import BIG_BOARD_SIZE, SMALL_BOARD_SIZE
from sgfmill import sgf

class TestLoading(unittest.TestCase):
    def setUp(self):
        self.games_dir = "games"
        self.game_files = find_game_files(self.games_dir)

    def test_load_random_games(self):
        print(self.game_files)
        for game_file in self.game_files:
            with self.subTest(game_file=game_file):
                try:
                    _, moves = load_game_moves(game_file)
                except KeyError as ke:
                    import os
                    import shutil
                    corrupted_dir = "corrupted"
                    if not os.path.exists(corrupted_dir):
                        os.makedirs(corrupted_dir)
                    corrupted_file_path = os.path.join(corrupted_dir, os.path.basename(game_file))
                    shutil.move(game_file, corrupted_file_path)

                self.assertIsNotNone(moves)
                self.assertIn("b", moves)
                self.assertIn("w", moves)

    def test_play_random_games(self):
        for game_file in self.game_files:
            with self.subTest(game_file=game_file):
                print(f"Testing for game file : {game_file}")
                file_winner, moves = load_game_moves(game_file)
                black_bot = ProgrammedBot(BLACK_STONE, moves["b"])
                white_bot = ProgrammedBot(WHITE_STONE, moves["w"])
                board = Game(board_size=BIG_BOARD_SIZE, players=[black_bot, white_bot], display=False)
                try:
                    board.play()
                except IndexError as ie:
                    print(game_file)
                    brm = black_bot.n_moves_remaining()
                    wrm = white_bot.n_moves_remaining()
                    if brm > wrm + 1:
                        raise ValueError("Number of remaining moves are not equal")


if __name__ == "__main__":
    unittest.main()
