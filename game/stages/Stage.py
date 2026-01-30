class Stage:
    # A stage consists of a group of enemies and a level X boundary. When the enemies are
    # defeated, the next stage begins
    def __init__(self, enemies, max_scroll_x, weapons=None, powerups=None, weather=None, music_track=None):
        self.enemies = enemies
        self.powerups = powerups or []
        self.max_scroll_x = max_scroll_x
        self.weapons = weapons or []
        self.weather = weather
        self.music_track = music_track


class BossStage(Stage):
    def __init__(self, boss, max_scroll_x, weapons=None, powerups=None, weather=None, music_track=None):
        super().__init__([boss], max_scroll_x, weapons=weapons, powerups=powerups, weather=weather, music_track=music_track)
        self.boss = boss
        self.intro_played = False
        # Fixed intro settings shared by all boss stages
        self.intro_walk_speed = 3.0
        self.intro_hold_frames = 250
        self.intro_overlay_alpha = 160
        self.intro_player_stop_offset = 220
