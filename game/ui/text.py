from pgzero.builtins import images

import pgzero
import pgzrun
import pygame

from game import config


# From Eggzy

font_mikachan_big = pygame.font.Font("fonts/mikachan-PB.otf", 40)
font_mikachan = pygame.font.Font("fonts/mikachan-PB.otf", 20)

def get_char_image_and_width(char):
    # Return width of given character. ord() gives the ASCII/Unicode code for the given character.
    if char == " ":
        return None, 22
    if char in config.SPECIAL_FONT_SYMBOLS_INVERSE:
        image = images.load(f"ui/{config.SPECIAL_FONT_SYMBOLS_INVERSE[char]}")
    else:
        image = images.load(f"{config.FONT_IMAGE_PREFIX}{ord(char)}")
    return image, image.get_width()

def get_char_image_width_and_height(char):
    # Return width of given character. ord() gives the ASCII/Unicode code for the given character.
    if char == " ":
        return None, 22, 50
    if char in config.SPECIAL_FONT_SYMBOLS_INVERSE:
        image = images.load(f"ui/{config.SPECIAL_FONT_SYMBOLS_INVERSE[char]}")
    else:
        image = images.load(f"{config.FONT_IMAGE_PREFIX}{ord(char)}")
    return image, image.get_width(), image.get_height()


def text_width(text):
    return sum([get_char_image_and_width(c)[1] for c in text])

def draw_text_otf(screen, text, x, y, font=font_mikachan, color= (0,0,0), italic=False, bold=False, underline=False):
    font.set_italic(italic)
    font.set_bold(bold)
    font.set_underline(underline)
    surf = font.render(text, True, color )
    screen.blit(surf, (x, y))

def draw_text_scaled(screen, text, X, Y, scale = 1):
    start_x = X

    for char in text:
        if char == "\n":
            # New line
            Y += 35
            X = start_x
        else:
            image, width, height = get_char_image_width_and_height(char)
            if image is not None:
                scaled_image = pygame.transform.scale(image, (width * scale, height * scale))
                screen.blit(scaled_image, (X, Y))
            X += width * scale

def draw_text(screen, text, x, y, centre=False):
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
