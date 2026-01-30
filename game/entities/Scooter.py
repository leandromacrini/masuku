from pygame import Vector2

from game.config import *
from game.actors.ScrollHeightActor import ScrollHeightActor
import game.runtime as runtime


class Scooter(ScrollHeightActor):
    def __init__(self, pos, facing_x, colour_variant):
        super().__init__(BLANK_IMAGE, pos, ("center",256))
        self.facing_x = facing_x
        self.colour_variant = colour_variant
        self.vel_x = -facing_x * 8
        self.frame = 0
        runtime.game.play_sound("sfx/scooter/scooter_fall")

    def update(self):
        self.frame += 1
        self.vpos.x += self.vel_x
        self.vel_x *= 0.94
        facing_id = 1 if self.facing_x > 0 else 0
        self.image = f"{SPRITE_DIRS['scooterboy']}/scooterboy_bike_{facing_id}_{min(self.frame // 30, 2)}_{self.colour_variant}"

    def get_draw_order_offset(self):
        return -1
