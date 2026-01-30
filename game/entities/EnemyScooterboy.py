import pygame
from random import randint
from pygame import Vector2

from game.config import *
from game.utils import *
from game.entities.Enemy import Enemy
from game.actors.Fighter import Fighter
from game.entities.Chain import Chain
from game.combat.attacks_data import ATTACKS
import game.runtime as runtime


class EnemyScooterboy(Enemy):
    SCOOTER_SPEED_SLOW = 4
    SCOOTER_SPEED_FAST = 12
    SCOOTER_ACCELERATION = 0.2

    def __init__(self, pos, start_timer=20):
        super().__init__(pos, "scooterboy", ("scooterboy_attack1",), start_timer=start_timer, approach_player_distance=ENEMY_APPROACH_PLAYER_DISTANCE_SCOOTERBOY, colour_variant=randint(0,2), score=30)
        self.state = Enemy.State.RIDING_SCOOTER
        self.scooter_speed = EnemyScooterboy.SCOOTER_SPEED_SLOW
        self.scooter_target_speed = self.scooter_speed
        self.scooter_sound_channel = None

    def spawned(self):
        super().spawned()
        try:
            self.scooter_sound_channel = pygame.mixer.find_channel()
            if self.scooter_sound_channel is not None:
                self.scooter_sound_channel.play(runtime.game.get_sound("sfx/scooter/scooter_slow"), loops=-1, fade_ms=200)
        except Exception as e:
            # Don't crash if no sound hardware
            pass

    def make_decision(self):
        # Scooterboy stays on scooter until knocked off
        if self.state != Enemy.State.RIDING_SCOOTER:
            super().make_decision()

    def determine_sprite(self):
        # Riding scooter is a state unique to Scooterboy, so it is dealt with here
        if self.state == Enemy.State.RIDING_SCOOTER:
            facing_id = 1 if self.facing_x == 1 else 0
            frame = 0
            if self.scooter_speed < self.scooter_target_speed:
                # Currently speeding up
                frame = min(self.frame // 5, 2)
            return f"characters/scooterboy/{self.sprite}_ride_{facing_id}_{frame}_{self.colour_variant}"
        else:
            return super().determine_sprite()

    def update(self):
        if self.state == Enemy.State.RIDING_SCOOTER:
            player = runtime.game.player

            # Change volume independently on left and right speakers
            if self.scooter_sound_channel is not None:
                left_volume = remap_clamp(abs(self.vpos.x - player.vpos.x + 500), 0, 1000, 1, 0)
                right_volume = remap_clamp(abs(self.vpos.x - player.vpos.x - 500), 0, 1000, 1, 0)
                self.scooter_sound_channel.set_volume(left_volume, right_volume)

            # Currently accelerating/decelerating?
            if self.scooter_speed != self.scooter_target_speed:
                self.scooter_speed, _ = move_towards(self.scooter_speed, self.scooter_target_speed, EnemyScooterboy.SCOOTER_ACCELERATION)
                self.frame += 1
            elif self.on_screen() and randint(0,30) == 0:
                # If on screen, random chance of accelerating
                self.scooter_target_speed = EnemyScooterboy.SCOOTER_SPEED_FAST
                if self.scooter_sound_channel is not None:
                    self.scooter_sound_channel.play(runtime.game.get_sound("sfx/scooter/scooter_accelerate", 6), loops=0, fade_ms=200)
                self.frame = 0

            # Move forward
            self.target.x = self.vpos.x + self.facing_x * self.scooter_speed
            self.vpos.x = self.target.x

            # Turn around if we've gone off the edge of the screen
            # We check self.x which is the actual screen position as opposed to the position in the scrolling level
            if (self.facing_x > 0 and self.x > WIDTH + 200) or (self.facing_x < 0 and self.x < -200):
                self.facing_x = -self.facing_x
                self.target.y = player.vpos.y

                # If player is standing, move to the same Y position as player, otherwise choose a random Y position
                # which is not close to the player Y position (to avoid player getting stunlocked)
                if runtime.game.player.falling_state == Fighter.FallingState.STANDING:
                    self.vpos.y = self.target.y
                else:
                    while abs(self.vpos.y - self.target.y) < 40:
                        self.vpos.y = randint(MIN_WALK_Y, HEIGHT-1)

                # Also slow down if at high speed
                self.scooter_target_speed = EnemyScooterboy.SCOOTER_SPEED_SLOW
                self.scooter_speed = self.scooter_target_speed

                # Go back to slow sound
                if self.scooter_sound_channel is not None:
                    self.scooter_sound_channel.play(runtime.game.get_sound("sfx/scooter/scooter_slow"), loops=-1, fade_ms=200)

            # Check to see if we hit the player
            if player.falling_state == Fighter.FallingState.STANDING \
              and abs(player.vpos.y - self.vpos.y) < 30 \
              and abs(self.vpos.x - player.vpos.x) < 60 \
              and player.height_above_ground < 20:
                player.hit(self, ATTACKS["scooter_hit"])

        elif self.just_knocked_off_scooter and self.scooter_sound_channel is not None and self.scooter_sound_channel.get_busy():
            self.scooter_sound_channel.stop()

        super().update()

    def override_walking(self):
        return self.state == Enemy.State.RIDING_SCOOTER

    def died(self):
        super().died()

        # Low chance of dropping a chain
        if randint(0, 19) == 0:
            runtime.game.weapons.append(Chain(self.vpos))

        # Stop scooter sound - only needed for when we're skipping stages in debug mode
        if self.scooter_sound_channel is not None and self.scooter_sound_channel.get_busy():
            self.scooter_sound_channel.stop()
