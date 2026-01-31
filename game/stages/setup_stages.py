from game import config
from game.entities.EnemyBoss import EnemyBoss
from game.entities.EnemyHoodie import EnemyHoodie
from game.entities.EnemyPortal import EnemyPortal
from game.entities.EnemyScooterboy import EnemyScooterboy
from game.entities.EnemyVax import EnemyVax
from game.entities.EnemyKasaobake import EnemyKasaobake
from game.entities.ExtraLifePowerup import ExtraLifePowerup
from game.entities.HealthPowerup import HealthPowerup
from game.entities.Barrel import Barrel
from game.stages.Stage import Stage, BossStage

STAGES = ()


def setup_stages():
    global STAGES
    STAGES = (
        Stage(max_scroll_x=0, enemies=[], weather={"type": "none"}, music_track="theme_jap"),

        Stage(max_scroll_x=1400,
              enemies=[EnemyHoodie(pos=(2100, 380))]
              ),

        BossStage(max_scroll_x=2400,
              boss=EnemyKasaobake(pos=(2800, 400)),
              music_track="final_boss",
              weather={"type": "rain", "intensity": 180, "wind": 0.0, "speed": 1.0, "length": 1.0, "ramp_seconds": 4.0},
            )              

    )
