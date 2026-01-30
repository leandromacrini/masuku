from random import randint

from game.entities.BreakableWeapon import BreakableWeapon
import game.runtime as runtime


class Chain(BreakableWeapon):
    def __init__(self, pos):
        super().__init__(pos, "chain", durability=randint(18, 25))

    def on_break(self):
        runtime.game.play_sound("sfx/weapons/chain_break")
