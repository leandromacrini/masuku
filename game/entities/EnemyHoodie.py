from random import randint
from pygame import Vector2

from game.entities.Enemy import Enemy
from game.entities.Stick import Stick
import game.runtime as runtime


class EnemyHoodie(Enemy):
    def __init__(self, pos, start_timer=20):
        super().__init__(pos, "hoodie", ("hoodie_lpunch", "hoodie_rpunch", "hoodie_special"), health=12, speed=Vector2(1.2, 1), start_timer=start_timer, colour_variant=randint(0,2), score=20)
        self.stand_frames = 2

    def died(self):
        super().died()

        # Chance of dropping a stick
        if randint(0, 2) == 0:
            runtime.game.weapons.append(Stick(self.vpos))
