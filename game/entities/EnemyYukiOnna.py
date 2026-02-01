from random import randint
from pygame import Vector2

from game.config import *
from game.utils import *
from game.entities.Enemy import Enemy
from game.entities.Mask import Mask
import game.runtime as runtime


class EnemyYukiOnna(Enemy):
    def __init__(self, pos, start_timer=20):
        super().__init__(pos, "onna", ("onna_fight", "onna_fight"),
                         speed=Vector2(0.5, 0.5), health=10, stamina=500, start_timer=start_timer,anchor_y=280,
                         score=200, enemy_type=Enemy.EnemyType.MID_BOSS)
        self.title_name = "雪女 (Yuki-onna)"
        self.boss_intro_image = "onna_boss_intro"

    def died(self):
        super().died()

        # Drop a mask
        runtime.game.powerups.append(Mask(self.vpos))