# Global runtime references shared across modules.

game = None
debug_drawcalls = []


def set_game(value):
    global game
    game = value


def get_game():
    return game
