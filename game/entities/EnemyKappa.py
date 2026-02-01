


from random import randint
from pygame import Vector2

from game.config import *
from game.utils import *
from game.entities.Enemy import Enemy
from game.entities.Mask import Mask
import game.runtime as runtime


class EnemyKappa(Enemy):
    def __init__(self, pos, start_timer=20):
        super().__init__(pos, "kappa", ("kappa_fight", "kappa_kick"),
                         speed=Vector2(0.5, 0.5), health=5, stamina=500, start_timer=start_timer,
                         score=20, enemy_type=Enemy.EnemyType.NORMAL)
