class Attack:
    def __init__(self, sprite=None, strength=None, anim_time=None, frame_time=5, frames=0, hit_frames=(),
                 recovery_time=0, reach=80, throw=False, grab=False, combo_next=None, flyingkick=False,
                 stamina_cost=10, rear_attack=False, stamina_damage_multiplier=1, stun_time_multiplier=1,
                 initial_sound=None, hit_sound=None):
        # Some data for attacks loaded from attacks.json must be modified to be in the format the game expects
        # For example, the keys in combo_next should be integers, but are strings in the json file as JSON only allows
        # string keys.
        if combo_next is not None:
            combo_next = {int(key): value for (key, value) in combo_next.items()}

        self.sprite = sprite
        self.strength = strength
        self.recovery_time = recovery_time  # Can't attack for this many frames after attack animation finishes
        self.anim_time = anim_time      # Frames for which animation plays, this allows us to stay on the last frame longer than previous frames
        self.frame_time = frame_time    # Frames for which each animation frame plays
        self.frames = frames            # Number of frames in animation
        self.hit_frames = hit_frames    # frames on which an opponent can be hit by this attack
        self.reach = reach              # Opponent must be closer than this for attack to hit
        self.throw = throw              # Is this an attack where we throw something, such as a barrel or the player?
        self.grab = grab                # Is this the attack where the boss grabs the player and throws him?
        self.combo_next = combo_next
        self.flying_kick = flyingkick
        self.stamina_cost = stamina_cost
        self.rear_attack = rear_attack
        self.stamina_damage_multiplier = stamina_damage_multiplier  # Does this attack do additional damage to the opponent's stamina?
        self.stun_time_multiplier = stun_time_multiplier
        self.initial_sound = initial_sound
        self.hit_sound = hit_sound
