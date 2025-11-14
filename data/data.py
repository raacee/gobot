from sgfmill import sgf


def extract_game_from_sgf(sgf_content) -> tuple[str | None, dict[str, list[tuple[int, int] | None]]]:
    # Parse the SGF content
    game = sgf.Sgf_game.from_string(sgf_content)
    winner = game.get_winner()
    win_method = game.get_root().get("RE")

    if "+" in win_method:
        win_method = win_method.split("+")[1]

    moves: dict[str, list[tuple[int, int]| None]] = {
        "b":[],
        "w":[]
    }

    for node in game.get_main_sequence():
        color, move = node.get_move()
        if color is not None:
            moves[color].append(move)

    return winner, win_method, moves


def get_winner(sgf_content):
     game = sgf.Sgf_game.from_string(sgf_content)
     return game.get_winner()
