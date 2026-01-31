from abc import ABC
from enum import Enum
from random import choice, randint

from pygame import Vector2

from game.config import *
from game.utils import *
from game.actors.Fighter import Fighter
from game.combat.attacks_data import ATTACKS
from game.entities.Barrel import Barrel
import game.runtime as runtime


class Enemy(Fighter, ABC):
    # State is an inner class - a class within a class, so its name doesn't clash with the global class State
    class State(Enum):
        APPROACH_PLAYER = 0
        GO_TO_POS = 1
        GO_TO_WEAPON = 2
        PAUSE = 3
        KNOCKED_DOWN = 4
        RIDING_SCOOTER = 5
        PORTAL = 6
        PORTAL_EXPLODE = 7
        IDLE = 8

    class EnemyType(Enum):
        NORMAL = 0
        MID_BOSS = 1
        FINAL_BOSS = 2

    def __init__(self, pos, name, attacks, start_timer,
                 speed=Vector2(1, 1),
                 health=15,
                 stamina=500,
                 approach_player_distance=ENEMY_APPROACH_PLAYER_DISTANCE,
                 anchor_y=256,
                 half_hit_area=Vector2(25, 20),
                 colour_variant=None,
                 hit_sound=None,
                 score=10,
                 enemy_type=EnemyType.NORMAL):
        # Slower animation speed than Hero
        super().__init__(pos, ("center",anchor_y), speed=speed, sprite=name, health=health, stamina=stamina,
                         anim_update_rate=14, half_hit_area=half_hit_area, colour_variant=colour_variant, hit_sound=hit_sound)

        # Target is a Vector2 instance
        # Must make a copy of the value, not a copy of the reference
        self.target = Vector2(self.vpos)

        self.target_weapon = None

        # Enemies don't try to target player until their start timer drops to zero
        # e.g. on starting a new stage we might not want them to start targeting the player until they have
        # scrolled onto the screen
        self.state = Enemy.State.PAUSE
        self.enemy_type = enemy_type
        self.title_name = name
        self.state_timer = start_timer

        self.attacks = attacks
        self.approach_player_distance = approach_player_distance
        self.score = score

    def spawned(self):
        # Called when the enemy is added into the game (when its stage is reached)
        pass

    def update(self):
        if self.state == Enemy.State.APPROACH_PLAYER:
            player = runtime.game.player

            # If player is attacking and we are quite close, chance (each frame) of backing up a little
            if player.attack_timer > 0 \
              and abs(self.vpos.y - player.vpos.y) < 20 \
              and abs(self.vpos.x - player.vpos.x) < 200 \
              and randint(0, 500) == 0:
                self.log("Back away from attack")
                self.target.x = self.vpos.x - self.facing_x * 90
                self.state = Enemy.State.GO_TO_POS
            else:
                # Head towards player
                # If we are holding a barrel, use a larger X offset so we throw from a distance
                if isinstance(self.weapon, Barrel):
                    x_offset = ENEMY_APPROACH_PLAYER_DISTANCE_BARREL
                else:
                    x_offset = self.approach_player_distance
                self.target.x = player.vpos.x + (x_offset * sign(self.vpos.x - player.vpos.x))
                self.target.y = player.vpos.y

        elif self.state == Enemy.State.GO_TO_POS:
            # In this state we just check to see if we've reached the target position, if so we make a new decision
            if self.target == self.vpos:
                self.make_decision()

        elif self.state == Enemy.State.GO_TO_WEAPON:
            if not self.target_weapon.can_be_picked_up() or not self.target_weapon.on_screen():
                # Weapon no longer available, make a new decision
                self.target_weapon = None
                self.make_decision()
            else:
                self.target = Vector2(self.target_weapon.vpos)
                if self.target == self.vpos:
                    # Arrived - pick up weapon and make new decision
                    self.log("Pick up weapon")
                    self.pickup_animation = self.target_weapon.name
                    self.frame = 0
                    self.target_weapon.pick_up(Fighter.WEAPON_HOLD_HEIGHT)
                    self.weapon = self.target_weapon
                    self.target_weapon = None
                    self.make_decision()

        elif self.state == Enemy.State.PAUSE:
            self.state_timer -= 1
            if self.state_timer < 0:
                self.make_decision()

        elif self.state == Enemy.State.KNOCKED_DOWN:
            # Check to see if we've got up again, if so switch state
            if self.falling_state == Fighter.FallingState.STANDING:
                self.make_decision()
        elif self.state == Enemy.State.IDLE:
            # Controlled externally (e.g. boss intro), no AI decisions.
            self.target = Vector2(self.vpos)
            self.walking = False

        # Update of RIDING_SCOOTER state is in EnemyScooterboy class

        if self.state == Enemy.State.APPROACH_PLAYER \
                or self.state == Enemy.State.GO_TO_POS \
                or self.state == Enemy.State.GO_TO_WEAPON:
            # Ensure that target position is within the level boundary
            self.target.x = max(self.target.x, runtime.game.boundary.left)
            self.target.x = min(self.target.x, runtime.game.boundary.right)
            self.target.y = max(self.target.y, runtime.game.boundary.top)
            self.target.y = min(self.target.y, runtime.game.boundary.bottom)

            # Check to see if another enemy is already heading for the new target pos, or one very close to it.
            # If so, make a new decision
            other_enemies_same_target = [enemy for enemy in runtime.game.enemies if enemy is not self and
                                         (enemy.target - self.target).length() < 20]
            if len(other_enemies_same_target) > 0:
                self.log("Same target")
                self.make_decision()

        # Call through to Fighter class update
        super().update()

    def draw(self, offset):
        super().draw(offset)

        if DEBUG_SHOW_TARGET_POS:
            screen.draw.line(self.vpos - offset, self.target - offset, (255,255,255))

    def determine_attack(self):
        # Allow attacking if we're in APPROACH_PLAYER state, aligned with player on Y axis, both I and player are
        # standing up, and we're within the right range of distances on the X axis, finally a must pass a random chance
        # check of 1 in 20
        # If we're holding a barrel, can be within any distance on the X axis

        # Unpack player pos into more convenient variables
        px, py = runtime.game.player.vpos

        holding_barrel = isinstance(self.weapon, Barrel)

        if self.state == Enemy.State.APPROACH_PLAYER \
               and runtime.game.player.falling_state == Fighter.FallingState.STANDING \
               and self.vpos.y == py \
               and (self.approach_player_distance * 0.9 < abs(self.vpos.x - px) <= self.approach_player_distance * 1.1 or
                    holding_barrel) \
               and randint(0,19) == 0:
            if self.weapon is not None:
                return ATTACKS[self.weapon.name]
            else:
                chosen_attack = ATTACKS[choice(self.attacks)]

                # If the chosen attack is a grab, don't allow it if the player is currently doing a flying kick
                if chosen_attack.grab and runtime.game.player.last_attack is not None and runtime.game.player.last_attack.flying_kick:
                    return None

                return chosen_attack

    def determine_pick_up_weapon(self):
        return False

    def determine_drop_weapon(self):
        return False

    def enemy_type(self):
        return Enemy.Type.NORMAL

    def get_opponents(self):
        return [runtime.game.player]

    def get_move_target(self):
        # Move towards player
        # Choose a location to walk to, depending on which side of the player we're on
        # We aim for a position 1 pixel above the player on the Y axis, so that we draw behind them
        # offset_x = 80 if self.vpos.x > runtime.game.player.vpos.x else -80
        # return runtime.game.player.vpos + Vector2(offset_x, -1)
        if self.target is None:
            # If no target, just return our current position
            return self.vpos
        else:
            #return self.target.get_pos()
            return self.target

    def get_desired_facing(self):
        # Always face towards player, unless we're on a scooter
        if self.state == Enemy.State.RIDING_SCOOTER:
            return self.facing_x
        else:
            return 1 if self.vpos.x < runtime.game.player.vpos.x else -1

    def hit(self, hitter, attack):
        if self.state == Enemy.State.KNOCKED_DOWN:
            # Already knocked down
            return
        if self.state == Enemy.State.IDLE:
            # Immune while retreating or idle
            return

        super().hit(hitter, attack)

        # If we're riding a scooter, then getting hit will always cause us to fall, regardless of stamina
        if self.state == Enemy.State.RIDING_SCOOTER:
            self.falling_state = Fighter.FallingState.FALLING
            self.frame = 0
            self.hit_timer = 0
            self.just_knocked_off_scooter = True

        if self.falling_state == Fighter.FallingState.FALLING:
            # Set state as knocked down
            self.state = Enemy.State.KNOCKED_DOWN
            self.log("Knocked down")

    def make_decision(self):
        if self.state == Enemy.State.IDLE:
            return
        player = runtime.game.player

        # If we're not going for a weapon:
        # If we're the only enemy, always move in to attack
        if len(runtime.game.enemies) == 1:
            self.log("Only enemy, go to player")
            self.state = Enemy.State.APPROACH_PLAYER
        else:
            # 7/10 chance of going directly to a point where we can attack the player, unless there's another enemy
            # already heading there in which case flank
            # 3/10 chance of going to a random point slightly further from the player
            # 1/10 chance of pausing for a short time

            r = randint(0, 9)
            if r < 7:
                # Check to see if another enemy on the same X side of the player is already heading to attack them
                # If so, flank instead
                other_enemies_on_same_side_attacking = [enemy for enemy in runtime.game.enemies if enemy is not self
                                                        and enemy.state == Enemy.State.APPROACH_PLAYER
                                                        and sign(enemy.vpos.x - player.vpos.x) == sign(self.vpos.x - player.vpos.x)]
                if len(other_enemies_on_same_side_attacking) > 0:
                    # Go to opposite side of player, at a Y position offset from them but on the same Y side that
                    # we're on now (e.g. if we're below, stay below). If Y pos is same, choose Y side randomly.
                    self.log("Begin flanking (same target)")
                    self.state = Enemy.State.GO_TO_POS
                    self.target.x = player.vpos.x - sign(self.vpos.x - player.vpos.x) * 50
                    self.target.y = player.vpos.y + sign(self.vpos.y - player.vpos.y) * 50
                    if self.target.y == player.vpos.y:
                        self.target.y = player.vpos.y + choice((-1,1)) * 50
                else:
                    # Go to player
                    self.log("Go to player")
                    self.state = Enemy.State.APPROACH_PLAYER

            elif r < 9:
                # Go to a random point at a moderate distance from the player
                # Stick to same half of screen on X axis
                self.log("Go to distance from player")
                x_side = sign(self.vpos.x - player.vpos.x)
                if x_side == 0:
                    x_side = choice((1,-1))
                x1 = int(player.vpos.x + (150 * x_side))
                x2 = int(player.vpos.x + (400 * x_side))
                x = randint(min(x1,x2), max(x1,x2))
                y = randint(runtime.game.boundary.top, runtime.game.boundary.bottom)
                self.target = Vector2(x, y)
                self.state = Enemy.State.GO_TO_POS

            else:
                # Pause
                self.log("Pause")
                self.state_timer = randint(50, 100)
                self.state = Enemy.State.PAUSE

    def should_remove(self):
        return self.lives <= 0
