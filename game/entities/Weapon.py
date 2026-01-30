from pygame import Vector2

from game.config import *
from game.actors.ScrollHeightActor import ScrollHeightActor
import game.runtime as runtime


class Weapon(ScrollHeightActor):
    def __init__(self, name, sprite, pos, end_pickup_frame, anchor=ANCHOR_CENTRE, bounciness=0, ground_friction=0.5, air_friction=0.996, separate_shadow=False):
        super().__init__(sprite, pos, anchor=anchor, separate_shadow=separate_shadow)
        self.name = name
        self.end_pickup_frame = end_pickup_frame
        self.held = False
        self.vel = Vector2(0,0)
        self.bounciness = bounciness
        self.ground_friction = ground_friction
        self.air_friction = air_friction

    def update(self):
        if not self.held:
            # If not held, check whether we're above the ground, or if we're moving
            if self.height_above_ground > 0 or self.vel.y != 0:
                # Fall to ground
                self.vel.y += WEAPON_GRAVITY
                if self.vel.y > self.height_above_ground:
                    # Bounce if we have bounciness, but stop bouncing if Y velocity is low
                    if self.bounciness > 0 and self.vel.y > 1:
                        # eg bounciness 1, height_above_ground 10, vel y 15, bounce amount should be 5
                        self.height_above_ground = abs(self.height_above_ground - self.vel.y) * self.bounciness
                        self.vel.y = -self.vel.y * self.bounciness
                        #print(f"{self.vel.y=}, {self.height_above_ground=}")
                    else:
                        self.height_above_ground = 0
                        self.vel.y = 0
                else:
                    # Didn't bounce - apply velocity to Y pos
                    self.height_above_ground -= self.vel.y

                assert(self.height_above_ground >= 0)

            self.vpos.x += self.vel.x

            # Friction on X axis, varies depending on whether we're on the ground or in the air
            friction = self.ground_friction if self.height_above_ground == 0 else self.air_friction
            self.vel.x *= friction
            if abs(self.vel.x) < 0.05:
                self.vel.x = 0

    def can_be_picked_up(self):
        return not self.held and self.height_above_ground == 0

    def pick_up(self, hold_height):
        assert(not self.held)
        self.held = True
        self.height_above_ground = hold_height   # for when we are dropped
        self.vel = Vector2(0, 0)
        self.image = BLANK_IMAGE

    def dropped(self):
        # Subclass has the responsibility of setting image to the correct sprite
        assert(self.held)
        self.held = False

    def used(self):
        pass

    def is_broken(self):
        return False
