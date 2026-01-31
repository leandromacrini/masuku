from __future__ import annotations

# UI sizes
HEALTH_STAMINA_BAR_WIDTH = 235
HEALTH_STAMINA_BAR_HEIGHT = 26

BOSS_HEALTH_STAMINA_BAR_WIDTH = 705
BOSS_HEALTH_STAMINA_BAR_HEIGHT = 26

INTRO_ENABLED = True

FLYING_KICK_VEL_X = 3
FLYING_KICK_VEL_Y = -8

JUMP_GRAVITY = 0.4
THROWN_GRAVITY = 0.025
WEAPON_GRAVITY = 0.5

BARREL_THROW_VEL_X = 4
BARREL_THROW_VEL_Y = 0

# For when player is thrown by boss
PLAYER_THROW_VEL_X = 5
PLAYER_THROW_VEL_Y = 0.5

# By default, the effect of an attack on the opponent's stamina is damage * 100
# Some attacks have an additional stamina damage multiplier
BASE_STAMINA_DAMAGE_MULTIPLIER = 100

# If stamina goes below zero, player can be knocked over more easily and minimum interval between attacks
# is longer
MIN_STAMINA = -100

DEBUG_LOGGING_ENABLED = False
DEBUG_SHOW_SCROLL_POS = False
DEBUG_SHOW_BOUNDARY = False
DEBUG_SHOW_ATTACKS = False
DEBUG_SHOW_TARGET_POS = False
DEBUG_SHOW_ANCHOR_POINTS = False
DEBUG_SHOW_HIT_AREA_WIDTH = False
DEBUG_SHOW_LOGS = False
DEBUG_SHOW_HEALTH_AND_STAMINA = False
DEBUG_PROFILING = False

# These symbols substitute for the controller button images when displaying text.
# The symbols representing these images must be ones that aren't actually used themselves, e.g. we don't use the
# percent sign in text
SPECIAL_FONT_SYMBOLS = {"xb_a": "%"}

# Create a version of SPECIAL_FONT_SYMBOLS where the keys and values are swapped
SPECIAL_FONT_SYMBOLS_INVERSE = {v: k for k, v in SPECIAL_FONT_SYMBOLS.items()}

WIDTH = 800
HEIGHT = 480

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

TITLE = "Masuku no Monogatari"

MIN_WALK_Y = 310

BOSS_NAME_X_POS = WIDTH * 0.20
BOSS_NAME_Y_POS = HEIGHT * 0.90 - BOSS_HEALTH_STAMINA_BAR_HEIGHT - 10
BOSS_HEALTH_BAR_X_POS = WIDTH * 0.06
BOSS_HEALTH_BAR_Y_POS = HEIGHT * 0.90

BOSS_COLOR_SHADOW = (0,0,0)
BOSS_COLOR_RED = (192, 43, 51)
BOSS_COLOR_RED_HEX = "#C02B33"

ENEMY_APPROACH_PLAYER_DISTANCE = 85
ENEMY_APPROACH_PLAYER_DISTANCE_SCOOTERBOY = 140
ENEMY_APPROACH_PLAYER_DISTANCE_BARREL = 180

ANCHOR_CENTRE = ("center", "center")
ANCHOR_CENTRE_BOTTOM = ("center", "bottom")

BACKGROUND_TILE_SPACING = 290

BACKGROUND_TILES_RAW = [
    # 1st row of TILE_DEMO+_3.png
    "wall_end1", "anime_alley1", "anime_alley2", "anime_alley1", "anime_alley2", "anime_alley1", "anime_alley2", "anime_alley1", "anime_alley2", "anime_alley1", "anime_alley2", "anime_alley1", "anime_alley2", "anime_alley1", "anime_alley2", "anime_alley1", "anime_alley2", "wall_end1", "wall_fill1", "wall_fill5", "wall_fill2", "alley1", "wall_end6", "wall_fill7",
    "wall_fill5", "alley2", "wall_end3", "wall_fill3", "wall_fill4", "wall_fill8", "alley5",
    "wall_end2", "alley3", "wall_end4", "wall_fill6",
    # row 2
    "alley6", "wall_end8", "wall_fill4", "alley7", "wall_end5", "alley8", "set_pc_a1", "set_pc_a2",
    "alley9", "set_pc_b1", "set_pc_b2", "set_pc_b3", "wall_end3", "wall_fill3", "alley8", "set_pc_a1",
    "set_pc_a2", "wall_fill2",
    # 3
    "con_start2", "con_end1a", "con_end2", "con_start2", "con_end1", "con_fill1", "con_end2a",
    "con_start2", "con_end1a", "con_fill1a", "con_end2", "set_pc_c1", "set_pc_c2", "set_pc_c3",
    "con_start1", "con_end1", "con_fill1", "con_fill2", "con_fill1a", "con_fill2a",
    # 4
    "wall_end1", "alley10", "steps_end1a", "steps_fill1a", "steps_fill2a", "steps_end2a",
    "flats_alley1", "steps_end1", "steps_end2", "flats_alley1", "flats_end1a", "steps_fill2",
    "steps_fill1", "flats_end2a", "flats_alley2", "set_pc_d1", "set_pc_d2", "set_pc_d3", "steps_end2a",
]

BACKGROUND_TILES = [f"backgrounds/tiles/{name}" for name in BACKGROUND_TILES_RAW]

BLANK_IMAGE = "misc/blank"
ITEMS_DIR = "items"
FONT_IMAGE_PREFIX = "ui/font/font0"

SPRITE_DIRS = {
    "hero": "characters/hero",
    "vax": "characters/vax",
    "hoodie": "characters/hoodie",
    "scooterboy": "characters/scooterboy",
    "boss": "characters/boss",
    "portal": "characters/portal",
    "kasaobake": "characters/kasaobake",
    "onna": "characters/onna",
    "kappa": "characters/kappa",
}
