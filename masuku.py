# Beat Streets - Code the Classics Volume 2
# Code by Andrew Gillett and Eben Upton
# Graphics by Dan Malone
# Music and sound effects by Allister Brimble
# https://github.com/raspberrypipress/Code-the-Classics-Vol2.git
# https://store.rpipress.cc/products/code-the-classics-volume-ii

# If the game window doesn't fit on the screen, you may need to turn off or reduce display scaling in the Windows/macOS settings
# On Windows, you can uncomment the following two lines to fix the issue. It sets the program as "DPI aware"
# meaning that display scaling won't be applied to it.
# import ctypes
# ctypes.windll.user32.SetProcessDPIAware()

import pgzero
import pgzrun
import pygame
import sys
from pygame import mixer
from pgzero.builtins import images, music

from game import config
from game.controls.KeyboardControls import KeyboardControls
from game.controls.JoystickControls import JoystickControls
from game.systems.Game import Game
from game.systems.State import State
from game.ui.text import draw_text
import game.runtime as runtime

# Check Python version number. sys.version_info gives version as a tuple, e.g. if (3,7,2,'final',0) for version 3.7.2.
# Unlike many languages, Python can compare two tuples in the same way that you can compare numbers.
if sys.version_info < (3, 6):
    print("This game requires at least version 3.6 of Python. Please download it from www.python.org")
    sys.exit()

# Check Pygame Zero version. This is a bit trickier because Pygame Zero only lets us get its version number as a string.
# So we have to split the string into a list, using '.' as the character to split on. We convert each element of the
# version number into an integer - but only if the string contains numbers and nothing else, because it's possible for
# a component of the version to contain letters as well as numbers (e.g. '2.0.dev0')
# This uses a Python feature called list comprehension
pgzero_version = [int(s) if s.isnumeric() else s for s in pgzero.__version__.split('.')]
if pgzero_version < [1, 2]:
    print(f"This game requires at least version 1.2 of Pygame Zero. You have version {pgzero.__version__}. Please upgrade using the command 'pip3 install --upgrade pgzero'")
    sys.exit()

# Pygame Zero uses these module-level constants
WIDTH = config.WIDTH
HEIGHT = config.HEIGHT
TITLE = config.TITLE

# Set up controls

def get_joystick_if_exists():
    return pygame.joystick.Joystick(0) if pygame.joystick.get_count() > 0 else None


def setup_joystick_controls():
    # We call this on startup, and keep calling it if no controller is present,
    # so a controller can be connected while the game is open
    global joystick_controls
    joystick = get_joystick_if_exists()
    joystick_controls = JoystickControls(joystick) if joystick is not None else None


def update_controls():
    keyboard_controls.update()
    # Allow a controller to be connected while the game is open
    if joystick_controls is None:
        setup_joystick_controls()
    if joystick_controls is not None:
        joystick_controls.update()


# Pygame Zero calls the update and draw functions each frame

def update():
    global state, game, total_frames, screen

    total_frames += 1

    update_controls()

    def button_pressed_controls(button_num):
        # Local function for detecting button 0 being pressed on either keyboard or controller, returns the controls
        # object which was used to press it, or None if button was not pressed
        for controls in (keyboard_controls, joystick_controls):
            # Check for fire button being pressed on each controls object
            # joystick_controls will be None if there no controller was connected on game startup,
            # so must check for that
            if controls is not None and controls.button_pressed(button_num):
                return controls
        return None

    if state == State.TITLE:
        # Check for start game
        if button_pressed_controls(0) is not None:
            state = State.CONTROLS

    elif state == State.CONTROLS:
        # Check for player starting game with either keyboard or controller
        controls = button_pressed_controls(0)
        if controls is not None:
            # Switch to play state, and create a new Game object, passing it the controls object which was used to start the game
            state = State.PLAY
            game = Game(controls)
            runtime.set_game(game)

    elif state == State.PLAY:
        game.update()
        if game.player.lives <= 0 or game.check_won():
            # Need to call game.shutdown to turn off scooter engine sound
            game.shutdown()
            state = State.GAME_OVER

    elif state == State.GAME_OVER:
        if button_pressed_controls(0) is not None:
            # Go back into title screen mode
            state = State.TITLE
            game = None
            runtime.set_game(None)


def draw():
    global screen

    if state == State.TITLE:
        # Draw logo
        logo_img = images.load("ui/title0") if total_frames // 20 % 2 == 0 else images.load("ui/title1")
        screen.blit(logo_img, (WIDTH // 2 - logo_img.get_width() // 2, HEIGHT // 2 - logo_img.get_height() // 2))

        draw_text(screen, f"PRESS {config.SPECIAL_FONT_SYMBOLS['xb_a']} OR Z", WIDTH // 2, HEIGHT - 50, True)

    elif state == State.CONTROLS:
        screen.fill((0, 0, 0))
        screen.blit("ui/menu_controls", (0, 0))

    elif state == State.PLAY:
        game.draw(screen)

    elif state == State.GAME_OVER:
        # Draw game over screen
        # Did player win or lose?
        if game.check_won():
            img = images.load("ui/status_win")
        else:
            img = images.load("ui/status_lose")
        screen.blit(img, (WIDTH // 2 - img.get_width() // 2, HEIGHT // 2 - img.get_height() // 2))


##############################################################################

# Set up sound system and start music
try:
    # Restart the Pygame audio mixer which Pygame Zero sets up by default. We find that the default settings
    # cause issues with delayed or non-playing sounds on some devices
    mixer.quit()
    mixer.init(44100, -16, 2, 1024)
    music.set_volume(0.3)

    music.play("intro")
except Exception:
    # If an error occurs (e.g. no sound hardware), ignore it
    pass


total_frames = 0

# Set up controls
keyboard_controls = KeyboardControls()
setup_joystick_controls()

# Set the initial game state
state = State.TITLE
game = None
runtime.set_game(None)

# Tell Pygame Zero to take over
pgzrun.go()
