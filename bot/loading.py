from data import extract_game_from_sgf
import os

def load_game_moves(file_path):
    with open(file_path, "tr") as f:
        winner, win_method, moves = extract_game_from_sgf(f.read())
    return winner, moves


def find_game_files(directory) -> list[str]:
    game_files: list[str] = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".sgf"):
                game_files.append(os.path.join(root, file))
    return game_files
