from pygame import Vector2
from random import randint

from game.entities.Enemy import Enemy


class EnemyVax(Enemy):
    def __init__(self, pos, start_timer=20):
        super().__init__(pos, "vax", ("vax_lpunch", "vax_rpunch", "vax_pound"), start_timer=start_timer, colour_variant=randint(0,2), score=20)
        self.stand_frames = 3
