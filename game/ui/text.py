from pgzero.builtins import images

import pgzero
import pgzrun
import pygame

from game import config


# From Eggzy

def get_char_image_and_width(char):
    # Return width of given character. ord() gives the ASCII/Unicode code for the given character.
    if char == " ":
        return None, 22
    if char in config.SPECIAL_FONT_SYMBOLS_INVERSE:
        image = images.load(f"ui/{config.SPECIAL_FONT_SYMBOLS_INVERSE[char]}")
    else:
        image = images.load(f"{config.FONT_IMAGE_PREFIX}{ord(char)}")
    return image, image.get_width()


def text_width(text):
    return sum([get_char_image_and_width(c)[1] for c in text])


def draw_text(text, x, y, centre=False):
    # Note that the centre option does not work correctly for text with line breaks
    if centre:
        x -= text_width(text) // 2

    start_x = x

    for char in text:
        if char == "\n":
            # New line
            y += 35
            x = start_x
        else:
            image, width = get_char_image_and_width(char)
            if image is not None:
                screen.blit(image, (x, y))
            x += width
