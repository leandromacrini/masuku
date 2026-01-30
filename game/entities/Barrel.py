from pygame import Vector2

from game.config import *
from game.combat.attacks_data import ATTACKS
from game.actors.Fighter import Fighter
from game.entities.Weapon import Weapon
import game.runtime as runtime


class Barrel(Weapon):
    def __init__(self, pos):
        super().__init__("barrel", f"{ITEMS_DIR}/barrel_upright", pos, end_pickup_frame=2, anchor=("center", 190), bounciness=0.75, ground_friction=0.96, separate_shadow=True)
        self.last_thrower = None
        self.frame = 0

    def update(self):
        # Call parent update
        super().update()

        # If moving, look for people to bash into
        # Won't collide if it can be picked up (if it is moving slowly enough)
        if not self.held and not self.can_be_picked_up() and self.vel.x != 0:
            for fighter in [runtime.game.player] + runtime.game.enemies:
                # Won't collide with the person who threw it
                # Won't collide with a fighter who is falling (incl. lying on the ground)
                # Must be within 30 pixels on X axis
                # Must be within 30 pixels on Y axis (vpos.y doesn't take height above ground into account, so this
                # is effectively the character's 'depth' in the level)
                # Must hit within the height of the character, taking into account height_above_ground for both the
                # barrel and fighter. The fighter may be able to jump over the barrel. The Y anchor of fighter sprites
                # is at the feet and the Y anchor of the barrel is at its centre.
                # The barrel isn't able to bounce above the head of a fighter (unless we added a really short fighter),
                # so we don't need to check that
                BARREL_HEIGHT = 40
                fighter_bottom_height = fighter.height_above_ground
                barrel_bottom_height = self.height_above_ground - (BARREL_HEIGHT // 2)
                barrel_top_height = barrel_bottom_height + BARREL_HEIGHT

                if fighter is not self.last_thrower \
                  and fighter.falling_state == Fighter.FallingState.STANDING \
                  and abs(fighter.vpos.y - self.vpos.y) < 30 \
                  and abs(self.vpos.x - fighter.vpos.x) < 30 \
                  and fighter_bottom_height < barrel_top_height:
                    fighter.hit(self, ATTACKS["barrel"])

            # Update rolling animation
            facing_id = 1 if self.vel.x > 0 else 0
            self.frame += 1
            self.image = f"{ITEMS_DIR}/barrel_roll_{facing_id}_{(self.frame // 14) % 4}"

    def throw(self, dir_x, thrower):
        self.dropped()
        self.vel.x = dir_x * BARREL_THROW_VEL_X
        self.vel.y = BARREL_THROW_VEL_Y
        self.last_thrower = thrower

        # Shift position for throw animation
        self.vpos.x += dir_x * 104
        #self.height_above_ground += 54

    def dropped(self):
        super().dropped()
        self.image = f"{ITEMS_DIR}/barrel_roll_0_0"

    def can_be_picked_up(self):
        return super().can_be_picked_up() and self.vel.length() < 1

    def get_draw_order_offset(self):
        # Consider barrel to be in front of another object with the same Y pos
        # (including player which has draw offset of 1)
        return 2
