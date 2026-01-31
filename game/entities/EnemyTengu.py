from random import randint
from pygame import Vector2

from game.config import *
from game.utils import *
from game.entities.Enemy import Enemy
from game.entities.Mask import Mask
import game.runtime as runtime


class EnemyTengu(Enemy):
    def __init__(self, pos, start_timer=20):
        super().__init__(pos, "tengu", ("tengu_lattack", "tengu_rattack", "tengu_special"),
                         speed=Vector2(0.5, 0.5), health=10, stamina=1000, start_timer=start_timer,
                         score=100, enemy_type=Enemy.EnemyType.MID_BOSS)
        self.title_name = "天狗 (Tengu)"
        self.boss_intro_image = "tengu_boss_intro"

    def died(self):
        super().died()

        # Drop a mask
        runtime.game.powerups.append(Mask(self.vpos))