from random import randint

from game.entities.BreakableWeapon import BreakableWeapon
import game.runtime as runtime


class Stick(BreakableWeapon):
    def __init__(self, pos):
        super().__init__(pos, "stick", durability=randint(12, 16))

    def on_break(self):
        runtime.game.play_sound("sfx/weapons/stick_break")
