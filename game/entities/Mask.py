from game.config import *
from game.entities.Powerup import Powerup
import game.runtime as runtime


class Mask(Powerup):
    def __init__(self, pos):
        super().__init__(pos, f"{ITEMS_DIR}/health_pickup")

    def collect(self, collector):
        super().collect(collector)

        # Add 20 health to the player who collected us, but don't go over their max health
        collector.health = min(collector.health + 20, collector.start_health)

        runtime.game.play_sound("sfx/ui/health", 1)