from pygame import Vector2

from game.config import *
from game.actors.Fighter import Fighter
import game.runtime as runtime


class Player(Fighter):
    def __init__(self, controls):
        # Anchor point just above bottom of sprite
        super().__init__(pos=(400, 400), anchor=("center",256), speed=Vector2(3,2), sprite="hero", health=30, lives=3, separate_shadow=True)
        self.controls = controls
        self.extra_life_timer = 0

    def update(self):
        super().update()

        self.extra_life_timer -= 1

        # Check for collecting powerups
        for powerup in runtime.game.powerups:
            if (powerup.vpos - self.vpos).length() < 30:
                powerup.collect(self)

    def draw(self, offset):
        super().draw(offset)
        # screen.draw.text(f"{self.vpos}", (0,0))
        # screen.draw.text(f"{self.vpos}", self.pos)

    def determine_attack(self):
        # Do we have a weapon?
        if self.weapon is not None:
            # Ensure we cannot attack during the pickup animation
            if self.pickup_animation is None and self.controls.button_pressed(0):
                return ATTACKS[self.weapon.name]

        elif self.controls.button_pressed(0):
            # in combo?
            if self.last_attack is not None and self.last_attack.combo_next is not None and self.attack_timer >= -30:
                # Get next attack in combo
                # 0 here represents button 0, ideally this code should be made more general, but in practice
                # the only combo we actually have is where you press button 0 three times to do a sequence of punches
                # ending in an uppercut
                if 0 in self.last_attack.combo_next:
                    return ATTACKS[self.last_attack.combo_next[0]]

            # Not in combo, just return default attack
            return ATTACKS["punch"]

        elif self.controls.button_pressed(1):
            return choice((ATTACKS["kick"], ATTACKS["highkick"]))

        elif self.controls.button_pressed(2):
            return ATTACKS["elbow"]

        elif self.controls.button_pressed(3):
            return ATTACKS["flyingkick"]

        return None

    def determine_pick_up_weapon(self):
        return self.controls.button_pressed(0)

    def determine_drop_weapon(self):
        return self.weapon is not None and self.controls.button_pressed(1)

    def get_opponents(self):
        return runtime.game.enemies

    def get_move_target(self):
        # Our target position is our current position offset based on control inputs and speed
        return self.vpos + Vector2(self.controls.get_x() * self.speed.x, self.controls.get_y() * self.speed.y)

    def get_desired_facing(self):
        dx = self.controls.get_x()
        if dx != 0:
            self.facing_x = sign(dx)
        else:
            # Keep facing same direction as before if no X input
            return self.facing_x

    def get_draw_order_offset(self):
        # Consider player to be in front of another object with the same Y pos
        return 1

    def gain_extra_life(self):
        self.lives += 1
        self.extra_life_timer = 30
