from random import randint, choice
from pygame import Vector2

from game.config import *
from game.entities.Enemy import Enemy
import game.runtime as runtime


class EnemyPortal(Enemy):
    GENERATE_ANIMATION_FRAMES = 6
    GENERATE_ANIMATION_DIVISOR = 16
    GENERATE_ANIMATION_TIME = GENERATE_ANIMATION_FRAMES * GENERATE_ANIMATION_DIVISOR

    def __init__(self, pos, enemies, spawn_interval, spawn_interval_change=0, max_spawn_interval=600, max_enemies=5, start_timer=90):
        # Hittable area is larger for portals
        super().__init__(pos, "portal", (), start_timer=start_timer, anchor_y=340, half_hit_area=Vector2(50, 50), hit_sound="sfx/portal/portal_hit")
        self.enemies = enemies
        self.spawn_interval = spawn_interval
        self.spawn_timer = spawn_interval
        self.spawn_interval_change = spawn_interval_change
        self.max_spawn_interval = max_spawn_interval
        self.max_enemies = max_enemies
        self.spawning_enemy = None
        self.spawn_facing = 0

    def spawned(self):
        super().spawned()
        runtime.game.play_sound("sfx/portal/portal_appear")

    def make_decision(self):
        # Like all enemies, portals start in the PAUSE state until their start_timer expires
        self.state = Enemy.State.PORTAL

    def determine_sprite(self):
        if self.state == Enemy.State.PAUSE and self.frame // 8 < 4:
            image = "portal_grow_" + str(min(self.frame // 8, 3))
        elif self.state == Enemy.State.PORTAL_EXPLODE:
            image = "portal_destroyed_" + str(min(self.frame // 6, 7))
        elif self.spawning_enemy is not None:
            # 3 frames of neutral generate animation, then 3 frames of animation for generating specific enemy
            frame = self.frame // EnemyPortal.GENERATE_ANIMATION_DIVISOR
            if frame < 3:
                image = "portal_generate_" + str(frame)
            else:
                frame = min(frame - 3, 2)
                image = f"portal_generate_{self.spawning_enemy.sprite}_{self.spawn_facing}_{frame}_{self.spawning_enemy.colour_variant}"
        elif self.hit_timer > 0:
            image = "portal_hit_0"
        else:
            image = "portal_idle_" + str((self.frame // 8) % 8)

        return f"{SPRITE_DIRS['portal']}/{image}"

    def update(self):
        self.frame += 1

        if self.state == Enemy.State.PORTAL:
            if self.health <= 0:
                self.state = Enemy.State.PORTAL_EXPLODE
                self.frame = 0
                runtime.game.play_sound("sfx/portal/portal_destroyed")

            else:
                self.spawn_timer -= 1
                if self.spawn_timer <= 0 and self.spawning_enemy is not None:
                    # Animation complete, actually put the enemy in the level
                    runtime.game.spawn_enemy(self.spawning_enemy)

                    self.spawning_enemy = None

                    # Reset spawn timer, depending on spawn_interval_change we may spawn less frequently as time goes on
                    self.spawn_interval += self.spawn_interval_change
                    self.spawn_interval = min(self.spawn_interval, self.max_spawn_interval)
                    self.spawn_timer = self.spawn_interval

                elif self.spawning_enemy is None and self.spawn_timer <= EnemyPortal.GENERATE_ANIMATION_TIME:
                    if len(runtime.game.enemies) >= self.max_enemies:
                        # Too many enemies to spawn at the moment, try again in one second
                        self.spawn_timer = 60
                    else:
                        # Randomly choose an enemy to spawn from our enemies list
                        chosen_enemy = choice(self.enemies)

                        # Choose direction for spawned enemy to face (0/1 = left/right)
                        self.spawn_facing = 0 if self.vpos.x > runtime.game.player.vpos.x else 1

                        # Instantiate the enemy, but it won't appear in the level until the animation is complete
                        self.spawning_enemy = chosen_enemy(self.vpos)

                        # Reset frame for spawning animation
                        self.frame = 0

                        runtime.game.play_sound("sfx/portal/portal_enemy_spawn")

        elif self.state == Enemy.State.PORTAL_EXPLODE:
            if self.frame > 50:
                self.lives -= 1
                self.died()

        super().update()

    def override_walking(self):
        # A portal never walks
        return True

# This is the scooter on its own, with the rider having been knocked off
