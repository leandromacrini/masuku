from game.config import *
from game.entities.Powerup import Powerup
import game.runtime as runtime


class ExtraLifePowerup(Powerup):
    def __init__(self, pos):
        super().__init__(pos, f"{ITEMS_DIR}/ingame_life9")
        self.timer = 0

    def update(self):
        super().update()
        self.timer += 1
        self.image = f"{ITEMS_DIR}/ingame_life" + str((self.timer // 2) % 10)

    def collect(self, collector):
        super().collect(collector)

        collector.gain_extra_life()

        runtime.game.play_sound("sfx/ui/health", 1)
