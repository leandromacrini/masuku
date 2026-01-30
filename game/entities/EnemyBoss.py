from random import randint
from pygame import Vector2

from game.config import *
from game.utils import *
from game.entities.Enemy import Enemy
from game.entities.Barrel import Barrel
import game.runtime as runtime


class EnemyBoss(Enemy):
    def __init__(self, pos, start_timer=20):
        super().__init__(pos, "boss", ("boss_lpunch", "boss_rpunch", "boss_kick", "boss_grab_player",),
                         speed=Vector2(0.9,0.8), health=25, stamina=1000, start_timer=start_timer, anchor_y=280,
                         half_hit_area=Vector2(30, 20), colour_variant=randint(0,2), score=75)
        self.stand_frames = 2

    def make_decision(self):
        # Boss can pick up a barrel, if they're not currently holding one
        # Look for a barrel we can walk to. Barrel must not be held by anyone else and must be on the screen
        if self.weapon is None:
            available_barrels = [weapon for weapon in runtime.game.weapons if isinstance(weapon, Barrel) and weapon.can_be_picked_up() and weapon.on_screen()]
            if len(available_barrels) > 0:
                # Find a weapon to go to
                for weapon in available_barrels:
                    # Don't go to a barrel if another enemy is already going to it
                    other_enemies_same_target = [enemy for enemy in runtime.game.enemies if enemy is not self and
                                                 enemy.target_weapon is weapon]
                    if len(other_enemies_same_target) == 0:
                        # This weapon is OK to go for
                        self.log("Go to weapon")
                        self.state = Enemy.State.GO_TO_WEAPON
                        self.target_weapon = weapon
                        return

        # If we didn't enter the GO_TO_WEAPON state, call the parent method
        super().make_decision()
