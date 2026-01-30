class Stage:
    # A stage consists of a group of enemies and a level X boundary. When the enemies are
    # defeated, the next stage begins
    def __init__(self, enemies, max_scroll_x, weapons=None, powerups=None, weather=None):
        self.enemies = enemies
        self.powerups = powerups or []
        self.max_scroll_x = max_scroll_x
        self.weapons = weapons or []
        self.weather = weather
