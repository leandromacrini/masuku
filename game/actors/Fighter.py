from abc import ABC, abstractmethod
from enum import Enum
from random import randint

from pygame import Vector2, Rect
import pgzero

from game.config import *
from game.utils import *
from game.actors.ScrollHeightActor import ScrollHeightActor
from game.combat.attacks_data import ATTACKS
from game.entities.Scooter import Scooter
import game.runtime as runtime


class Fighter(ScrollHeightActor, ABC):
    WEAPON_HOLD_HEIGHT = 100

    class FallingState(Enum):
        STANDING = 0
        FALLING = 1
        GETTING_UP = 2
        GRABBED = 3
        THROWN = 4

    def log(self, str):
        if DEBUG_LOGGING_ENABLED:
            l = f"{runtime.game.timer} {str} {self.vpos}"
            print(self, l)
            self.logs.append(l)

    def __init__(self, pos, anchor, speed, sprite, health, anim_update_rate=8, stamina=500, half_hit_area=Vector2(25, 20), lives=1, colour_variant=None, separate_shadow=False, hit_sound=None):
        super().__init__(BLANK_IMAGE, pos, anchor, separate_shadow=separate_shadow)

        # Speed is a Vector2 containing x and y speed
        self.speed = speed

        # e.g. "hero" or "enemy"
        self.sprite = sprite

        self.anim_update_rate = anim_update_rate
        self.stand_frames = 2

        self.facing_x = 1

        # Updates each game frame, then is translated into an animation frame number depending on the animation
        # being played
        self.frame = 0

        # Last attack is current attack if attack_timer is above zero
        self.last_attack = None

        # Above zero = currently attacking, zero or below = time since last attack
        self.attack_timer = 0

        # Are we knocked down or in the process of being knocked down?
        self.falling_state = Fighter.FallingState.STANDING

        # Are we currently walking? Used to determine whether to use standing or walking animation
        self.walking = False

        self.vel = Vector2(0, 0)  # Velocity X used when falling or being pushed backwards or for flying kick, velocity Y for jumping

        self.pickup_animation = None

        self.hit_timer = 0      # if above 0, we've just been hit and are doing the animation where we recoil from that
        self.hit_frame = 0

        self.stamina = stamina
        self.max_stamina = stamina

        # Determines whether an opponent's attack will hit us, based on the distance between us and the attack's reach
        # Larger number for the portal, because the portal is physically bigger
        self.half_hit_area = half_hit_area

        self.health = health
        self.start_health = health
        self.lives = lives

        # Used for enemies with multiple colour variants - appended to sprite name
        self.colour_variant = colour_variant

        self.hit_sound = hit_sound

        self.weapon = None

        # Used for animation where Scooterboy enemy is knocked off his scooter
        self.just_knocked_off_scooter = False

        self.use_die_animation = False

        self.logs = []

    def update(self):
        self.attack_timer -= 1

        # Apply gravity and velocity if in air
        if self.height_above_ground > 0 or self.vel.y != 0:
            self.vpos.x += self.vel.x
            self.vel.y += THROWN_GRAVITY if self.falling_state == Fighter.FallingState.THROWN else JUMP_GRAVITY
            self.height_above_ground -= self.vel.y
            self.apply_movement_boundaries(self.vel.x, 0)
            if self.height_above_ground < 0:
                self.height_above_ground = 0
                self.vel.x = 0
                self.vel.y = 0

                # Don't do the been hit animation after landing (from flying kick or from being thrown)
                self.hit_timer = 0

        # Update logic and animation based on current situation - falling, getting up, hit, pickup animation, or normal
        # walking/standing/attacking

        # Check for falling and dying
        # Portals don't fall when they die, so the logic for them dying is within their class
        if self.falling_state == Fighter.FallingState.FALLING:
            # Get pushed backwards
            self.vpos.x += self.vel.x
            self.vel.x, _ = move_towards(self.vel.x, 0, 0.5)

            self.apply_movement_boundaries(self.vel.x, 0)

            self.frame += 1

            if self.frame > 120:
                # If we're not yet out of health, get up and reset stamina
                if self.health > 0:
                    self.falling_state = Fighter.FallingState.GETTING_UP
                    self.frame = 0
                    self.stamina = self.max_stamina
                else:
                    # If we're out of health, flash on and off for a short while, then lose a life
                    if self.frame > 240:
                        self.lives -= 1

                        # If we still have lives left, get up
                        if self.lives > 0:
                            self.health = self.start_health
                            self.falling_state = Fighter.FallingState.GETTING_UP
                            self.frame = 0
                            self.stamina = self.max_stamina
                            self.use_die_animation = False
                        else:
                            self.died()

        elif self.falling_state == Fighter.FallingState.GETTING_UP:
            self.frame += 1
            self.vpos.x += 0.1 * self.facing_x     # Move forward slightly as we get up
            if self.frame > 20:
                self.falling_state = Fighter.FallingState.STANDING
                self.frame = 0

        elif self.falling_state == Fighter.FallingState.THROWN:
            self.frame += 1
            if self.height_above_ground <= 0:
                self.falling_state = Fighter.FallingState.FALLING
                self.frame = 80

        elif self.hit_timer > 0:
            # Playing the 'hit' animation, briefly stunned
            self.hit_timer -= 1

        elif self.pickup_animation is not None:
            # Doing animation for picking up a weapon
            self.frame += 1
            if self.frame > 30:
                self.pickup_animation = None

        elif self.override_walking():
            # If this is the case, we're in some kind of special state, managed by a subclass, which means we shouldn't
            # do the usual walking/attacking behaviour below - e.g. Scooterboy riding scooter
            pass

        elif self.falling_state == Fighter.FallingState.STANDING:
            # Standing, walking or attacking

            # Recover stamina over time
            if self.stamina < self.max_stamina:
                self.stamina += 1

            # Update position of held weapon
            # The weapon actor is invisible while being held as we switch to a different fighter sprite using the
            # weapon, but we update weapon pos so that if we drop the weapon, it reappears as a distinct sprite in the
            # correct location
            if self.weapon is not None:
                self.weapon.vpos = self.vpos + Vector2(self.facing_x * 20, 0)

            # Are we ready to attack or pick up/drop a weapon?
            # If we're out of stamina, recovery time will be longer
            last_attack_recovery_time = 0 if not self.last_attack else self.last_attack.recovery_time
            if self.stamina <= 0:
                last_attack_recovery_time *= 3
            if self.attack_timer <= -last_attack_recovery_time:
                # Not currently attacking, do we want to start attacking?

                # Before deciding if we want to attack - do we instead want to pick up or drop a weapon?
                if self.weapon is None:
                    # Find weapons within reach
                    nearby_weapons = [weapon for weapon in runtime.game.weapons if (weapon.vpos - self.vpos).length() < 50]
                    if len(nearby_weapons) > 0:
                        if self.determine_pick_up_weapon():
                            # Sort nearby weapons by distance. length_squared is used to order them instead of
                            # length as it is more efficient
                            nearby_weapons.sort(key=lambda weapon: (weapon.vpos - self.vpos).length_squared())
                            for weapon in nearby_weapons:
                                if weapon.can_be_picked_up():
                                    self.pickup_animation = weapon.name
                                    self.frame = 0
                                    self.weapon = weapon
                                    weapon.pick_up(Fighter.WEAPON_HOLD_HEIGHT)
                                    break
                else:
                    # Drop weapon?
                    if self.determine_drop_weapon():
                        self.drop_weapon()

                # Attack? Only allow if we didn't just start picking up a weapon!
                if self.pickup_animation is None:
                    attack = self.determine_attack()
                    if attack is not None:
                        self.log("Attack " + attack.sprite)
                        self.last_attack = attack
                        self.attack_timer = attack.anim_time
                        self.stamina -= attack.stamina_cost
                        self.stamina = max(self.stamina, MIN_STAMINA)
                        self.frame = 0

                        if attack.initial_sound is not None:
                            # * = unpack the elements of the tuple (sound to play, and number of variations) into
                            # arguments to pass to play_sound
                            runtime.game.play_sound(*attack.initial_sound)

                        # Is this a flying kick?
                        if attack.flying_kick:
                            self.vel.x = FLYING_KICK_VEL_X * self.facing_x
                            self.vel.y = FLYING_KICK_VEL_Y

                        # Grab player?
                        if attack.grab:
                            runtime.game.player.grabbed()

            # Update movement and animation, and pick up a weapon if desired
            # Must check attack_timer again as an attack may only just have started during the previous block of code
            if self.attack_timer <= 0:
                # Not attacking
                # Update facing_x. If get_desired_facing returns None, leave facing_x as it is
                desired_facing = self.get_desired_facing()
                if desired_facing is not None:
                    self.facing_x = desired_facing

                target = self.get_move_target()
                if target != self.vpos:
                    self.walking = True

                    self.vpos.x, dx = move_towards(self.vpos.x, target.x, self.speed.x)
                    self.vpos.y, dy = move_towards(self.vpos.y, target.y, self.speed.y)

                    self.apply_movement_boundaries(dx, dy)

                    self.frame += 1

                else:
                    # No movement, reset frame to standing
                    self.walking = False
                    self.frame += 1  # Resetting frame to 7 rather than zero fixes an issue where it looks weird if you only walk for a fraction of a second
            else:
                # Currently attacking
                self.frame += 1

                frame = self.get_attack_frame()

                # If current frame of attack is a hit frame, inflict damage to enemies
                if frame in self.last_attack.hit_frames:
                    # Is this a throw attack?
                    if self.last_attack.throw:
                        # If the current attack is a grab attack, that means we're the boss throwing the player
                        if self.last_attack.grab:
                            # Throw the player, if we haven't already done that on a previous frame
                            if runtime.game.player.falling_state == Fighter.FallingState.GRABBED:
                                runtime.game.player.hit(self, self.last_attack)
                                runtime.game.player.thrown(self.facing_x)

                        # Otherwise it's a normal throw of a barrel - make sure we still have the weapon, might have
                        # released it on a previous frame!
                        elif self.weapon is not None:
                            self.weapon.throw(self.facing_x, self)
                            self.weapon = None

                    # Call attack regardless of whether this is a throw attack, this fixes an issue where the barrel
                    # doesn't hit opponents because the position it's in when it's released is already past them
                    self.attack(self.last_attack)

    def attack(self, attack):
        # See if there is an opponent directly in front of us who we can hit (or behind us if it's a rear attack
        # such as elbow)
        if attack.strength > 0:
            # Loop through all opponents to see which (if any) this attack should hit
            for opponent in self.get_opponents():
                vec = opponent.vpos - self.vpos
                facing_correct = sign(self.facing_x) == sign(vec.x)
                if attack.rear_attack:
                    facing_correct = not facing_correct

                # Should attack hit this opponent?
                if abs(vec.y) < opponent.half_hit_area.y and facing_correct and abs(vec.x) < attack.reach + opponent.half_hit_area.x:
                    opponent.hit(self, attack)

                    # If we're using a weapon, it may have broken as a result of being used
                    if self.weapon is not None and self.weapon.is_broken():
                        self.drop_weapon()

            if DEBUG_SHOW_ATTACKS:
                attack_facing = self.facing_x * (-1 if attack.rear_attack else 1)
                debug_rect = Rect(self.x - (attack.reach if attack_facing == -1 else 0), self.y - 5, attack.reach, 10)
                runtime.debug_drawcalls.append(lambda: screen.draw.filled_rect(debug_rect, (255, 0, 0)))

    def hit(self, hitter, attack):
        # Hitter can be another fighter, or a weapon such as a barrel
        # Can't be hit if we're falling/getting up
        if self.falling_state == Fighter.FallingState.STANDING or self.falling_state == Fighter.FallingState.GRABBED:
            # Can't be hit if we're already in the hit animation
            if self.hit_timer <= 0:
                self.stamina -= attack.strength * BASE_STAMINA_DAMAGE_MULTIPLIER * attack.stamina_damage_multiplier
                self.stamina = max(self.stamina, MIN_STAMINA)
                self.health -= attack.strength

                # Hit timer ensures we can't receive damage again until it's counted down, and stuns the fighter
                # Stronger attacks stun for longer
                self.hit_timer = attack.strength * 8 * attack.stun_time_multiplier
                self.hit_frame = randint(0, 1)

                # Stop our attack if we're in the middle of one - unless it's a flying kick, in which case continue.
                # Code elsewhere will ensure we don't do the 'been hit' animation at the end of a flying kick
                if self.attack_timer > 0 and (self.last_attack is not None and not self.last_attack.flying_kick):
                    self.attack_timer = 0

                # Drop weapon
                if self.weapon is not None:
                    self.drop_weapon()

                if attack.hit_sound is not None:
                    # * = unpack the elements of the tuple (sound to play, and number of variations) into
                    # arguments to pass to play_sound
                    runtime.game.play_sound(*attack.hit_sound)

                if self.hit_sound is not None:
                    # Sound for me being hit (only used by portal)
                    runtime.game.play_sound(self.hit_sound)

                # Check for being knocked down due to being out of health or stamina
                # Portals can't fall
                if (self.stamina <= 0 or self.health <= 0) and self.__class__.__name__ != "EnemyPortal":
                    self.falling_state = Fighter.FallingState.FALLING
                    self.frame = 0
                    self.hit_timer = 0

                    # If we're knocked down due to being out of stamina, and we're close to death, just die already
                    if self.health < 3:
                        self.health = 0
                        self.use_die_animation = (randint(0,1) == 0)    # Use die animation 50% of the time

                # If the attacker was using a weapon, tell the weapon that it was used
                # Must check that hitter is a Fighter, as it might be a barrel!
                if isinstance(hitter, Fighter) and hitter.weapon is not None:
                    hitter.weapon.used()

            # Always face towards hitter
            # First check to make sure that hitter and I aren't at the same X position
            if hitter.vpos.x != self.vpos.x:
                self.facing_x = sign(hitter.vpos.x - self.vpos.x)

                if self.falling_state == Fighter.FallingState.FALLING and not self.use_die_animation:
                    # Get knocked backwards
                    self.vel.x += -self.facing_x * 10

    def died(self):
        # Called when out of lives, can be overridden in cases where subclasses need to know that - e.g.
        # EnemyHoodie may drop stick on death
        pass

    def draw(self, offset):
        # Determine sprite to use based on our current action
        z = self.determine_sprite()

        super().draw(offset)

        if DEBUG_SHOW_HEALTH_AND_STAMINA:
            text = f"HP: {self.health}\nSTM: {self.stamina}"
            screen.draw.text(text, fontsize=24, center=(self.x, self.y - 200), color="#FFFFFF", align="center")

        if DEBUG_SHOW_HIT_AREA_WIDTH:
            screen.draw.rect(Rect(self.x - self.half_hit_area.x, self.y - self.half_hit_area.y, self.half_hit_area.x * 2, self.half_hit_area.y * 2), (255,255,255))

        if DEBUG_SHOW_LOGS:
            y = self.y
            for l in reversed(self.logs):
                screen.draw.text(l, fontsize=14, center=(self.x, y), color="#FFFFFF", align="center")
                y += 10

    def determine_sprite(self):
        show = True

        if self.falling_state == Fighter.FallingState.FALLING:
            if self.frame > 60 and self.health <= 0 and (self.frame // 10) % 2 == 0:
                # If we're out of health, flash on and off for a short while
                show = False

            if show:
                # When we fall down, we stay on the last frame (2) for an extended period
                # If we've only just fallen off a scooter, play knocked_off frame 0 before
                # continuing from knockdown frame 1
                if self.just_knocked_off_scooter:
                    # Check if we need to transition to the knockdown stage of the animation
                    if self.frame > 10:
                        self.just_knocked_off_scooter = False

                        # Create the scooter as an independent object
                        runtime.game.scooters.append(Scooter(self.vpos, self.facing_x, self.colour_variant))

                # Now choose the sprite to use this frame
                if self.just_knocked_off_scooter:
                    anim_type = "knocked_off"
                    frame = 0
                elif self.use_die_animation:
                    anim_type = "die"
                    frame = min(self.frame // 20, 2)
                else:
                    last_frame = 3 if self.__class__.__name__ == "EnemyScooterboy" else 2
                    anim_type = "knockdown"
                    frame = min(self.frame // 10, last_frame)

        elif self.falling_state == Fighter.FallingState.GETTING_UP:
            anim_type = "getup"
            frame = min(self.frame // 10, 1)

        elif self.falling_state == Fighter.FallingState.GRABBED:
            show = False

        elif self.falling_state == Fighter.FallingState.THROWN:
            anim_type = "thrown"
            frame = min(self.frame // 12, 3)

        elif self.hit_timer > 0:
            frame = self.hit_frame
            anim_type = "hit"

        elif self.pickup_animation is not None:
            # Doing animation for picking up a weapon
            frame = min(self.frame // 12, self.weapon.end_pickup_frame)
            anim_type = f"pickup_{self.pickup_animation}"

        elif self.attack_timer > 0:
            # Currently attacking
            anim_type = self.last_attack.sprite
            frame = self.get_attack_frame()

        else:
            # Walking or standing
            if self.walking:
                # There are four walk animation frames, we take self.frame (an unbounded number incrementing by 1 each
                # game frame) and divide it by self.anim_update_rate (giving that many frames of delay between
                # switching animation frames), the result of that is MODded 4 to reduce it to the actual animation
                # frame to use in the range 0-3
                anim_type = "walk"
                frame = (self.frame // self.anim_update_rate) % 4  # 4 frames of walking animation
            else:
                # Standing
                # Use anim_type stand or walk depending on whether we have a weapon - we only have 'walk' sprites
                # for weapons
                if(self.weapon is None):
                    anim_type = "stand"
                    frame = (self.frame // self.anim_update_rate) % self.stand_frames
                else:
                    anim_type = "walk"
                    frame = 0
                

            # Add the weapon name to the walking/standing animation
            # This isn't done for weapon attack animations, because barrel is released during the throw animation
            anim_type += ("_" + self.weapon.name) if self.weapon is not None else ""

        if show:
            # In sprite filenames, 0 = facing left, 1 = right
            facing_id = 1 if self.facing_x == 1 else 0
            image = f"{self.sprite}_{anim_type}_{facing_id}_{frame}"
            if self.colour_variant is not None:
                image += "_" + str(self.colour_variant)
            sprite_dir = SPRITE_DIRS.get(self.sprite, "")
            if sprite_dir:
                image = f"{sprite_dir}/{image}"
        else:
            image = BLANK_IMAGE

        return image

    def get_attack_frame(self):
        # return value of this function is an animation frame, e.g. we are on the third frame of the punch animation
        # self.frame is a game frame, increasing by 1 every 1/60th of a second
        # We use self.last_attack to get the current attack that we're doing, i.e. it's the last attack we started
        # doing, and we're still doing it
        frame = (self.frame // self.last_attack.frame_time)
        frame = min(frame, self.last_attack.frames - 1)
        return frame

    def override_walking(self):
        # Used by subclasses to prevent the usual walking/attacking behaviour
        return False

    def drop_weapon(self):
        self.pickup_animation = None    # Stop pickup animation if we're in the middle of one
        self.weapon.dropped()
        self.weapon = None

    def grabbed(self):
        self.log("Grabbed")
        self.falling_state = Fighter.FallingState.GRABBED
        if self.weapon is not None:
            self.drop_weapon()

    def thrown(self, dir_x):
        self.log("Thrown")
        self.falling_state = Fighter.FallingState.THROWN
        self.vel.x = dir_x * PLAYER_THROW_VEL_X
        self.vel.y = PLAYER_THROW_VEL_Y
        self.facing_x = -dir_x

        # Shift position for throw animation
        self.vpos.x += dir_x * 50
        self.height_above_ground = 45

    def apply_movement_boundaries(self, dx, dy):
        # A fighter outside the boundary can walk in a direction which will help them get inside the boundary, but not
        # in the direction that will take them further out of it
        if dx < 0 and self.vpos.x < runtime.game.boundary.left:
            self.vpos.x = runtime.game.boundary.left
        elif dx > 0 and self.vpos.x > runtime.game.boundary.right:
            self.vpos.x = runtime.game.boundary.right
        if dy < 0 and self.vpos.y < runtime.game.boundary.top:
            self.vpos.y = runtime.game.boundary.top
        elif dy > 0 and self.vpos.y > runtime.game.boundary.bottom:
            self.vpos.y = runtime.game.boundary.bottom

    # Every class that inherits from Fighter must implement each of the following abstract methods

    @abstractmethod
    def determine_attack(self):
        pass

    @abstractmethod
    def determine_pick_up_weapon(self):
        pass

    @abstractmethod
    def determine_drop_weapon(self):
        pass

    @abstractmethod
    def get_opponents(self):
        pass

    @abstractmethod
    def get_move_target(self):
        pass

    @abstractmethod
    def get_desired_facing(self):
        pass
