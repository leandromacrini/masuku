from abc import abstractmethod
from game.config import *
from game.entities.Weapon import Weapon
import game.runtime as runtime


class BreakableWeapon(Weapon):
    def __init__(self, pos, name, durability):
        super().__init__(name, f"{ITEMS_DIR}/{name}", pos, end_pickup_frame=1, anchor=("center", "center"))
        self.break_counter = durability

    def dropped(self):
        super().dropped()
        self.image = f"{ITEMS_DIR}/{self.name}"

    def get_draw_order_offset(self):
        # Used for stick/chain on ground. Default draw order means it is sometimes drawn on top of a character standing on
        # it, but changing Y anchor point also has some undesirable effects
        return -50

    def used(self):
        self.break_counter -= 1
        if self.break_counter == 0:
            self.on_break()

    def is_broken(self):
        return self.break_counter <= 0

    @abstractmethod
    def on_break(self):
        # Can't call this break as that's a keyword in Python!
        pass
