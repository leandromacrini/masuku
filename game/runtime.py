# Global runtime references shared across modules.

game = None
screen = None
weather = None

debug_drawcalls = []


def set_game(value):
    global game
    game = value


def get_game():
    return game


def set_screen(value):
    global screen
    screen = value


def get_screen():
    return screen


def set_weather(value):
    global weather
    weather = value


def get_weather():
    return weather

