from game import config
from game.entities.EnemyBoss import EnemyBoss
from game.entities.EnemyHoodie import EnemyHoodie
from game.entities.EnemyPortal import EnemyPortal
from game.entities.EnemyScooterboy import EnemyScooterboy
from game.entities.EnemyVax import EnemyVax
from game.entities.EnemyKasaobake import EnemyKasaobake
from game.entities.EnemyYukiOnna import  EnemyYukiOnna
from game.entities.ExtraLifePowerup import ExtraLifePowerup
from game.entities.HealthPowerup import HealthPowerup
from game.entities.Barrel import Barrel
from game.stages.Stage import Stage, BossStage

STAGES = ()

def setup_stages():
      global STAGES
      STAGES = (
            Stage(max_scroll_x=0, enemies=[], weather=None, music_track="theme_jap"),

            Stage(max_scroll_x=1400,
                  enemies=[EnemyHoodie(pos=(2100, 380))]
            ),

            BossStage(max_scroll_x=2400,
                  boss=EnemyYukiOnna(pos=(2800, 400)),
                  music_track="final_boss",
                  weather="leaves",
            )
      )     

def setup_stages2():
    global STAGES
    STAGES = (
        Stage(max_scroll_x=0, enemies=[], weather=None, music_track="theme_jap"),

        Stage(max_scroll_x=600,
              enemies=[EnemyVax(pos=(1400, 400)),
                       EnemyHoodie(pos=(1500, 500))],
              weapons=[Barrel((1600, 400))]),

        Stage(max_scroll_x=600,
              enemies=[EnemyScooterboy(pos=(200, 400))]),

        Stage(max_scroll_x=900,
              enemies=[EnemyBoss(pos=(1800, 400)),
                       EnemyVax(pos=(400, 400))]),

        Stage(max_scroll_x=1400,
              enemies=[EnemyHoodie(pos=(2100, 380)),
                       EnemyHoodie(pos=(2100, 480)),
                       EnemyHoodie(pos=(800, 420))],
              powerups=[HealthPowerup(pos=(2300, config.MIN_WALK_Y))]
              ),

        Stage(max_scroll_x=1900,
              enemies=[EnemyVax(pos=(2400, 380)),
                       EnemyHoodie(pos=(2500, 480)),
                       EnemyScooterboy(pos=(2800, 400))]),

        Stage(max_scroll_x=2500,
              enemies=[EnemyScooterboy(pos=(3800, 380)),
                       EnemyScooterboy(pos=(3300, 480)),
                       EnemyScooterboy(pos=(1200, 400))]),

        Stage(max_scroll_x=3000,
              enemies=[EnemyVax(pos=(4000, 380)),
                       EnemyVax(pos=(3900, 480)),
                       EnemyVax(pos=(4200, 460)),
                       EnemyVax(pos=(4200, 450)),
                       EnemyHoodie(pos=(3900, 300)),
                       EnemyHoodie(pos=(3950, 320))]),

        Stage(max_scroll_x=3600,
              enemies=[EnemyVax(pos=(4600, 380)),
                       EnemyScooterboy(pos=(1200, 350)),
                       EnemyScooterboy(pos=(1400, 350)),
                       EnemyScooterboy(pos=(1600, 350)),
                       EnemyScooterboy(pos=(1800, 350)),
                       EnemyScooterboy(pos=(2000, 350))],
              powerups=[HealthPowerup(pos=(5100, config.MIN_WALK_Y))]
              ),

        Stage(max_scroll_x=4600,
              enemies=[EnemyHoodie(pos=(4800, 380)),
                       EnemyHoodie(pos=(4800, 350)),
                       EnemyScooterboy(pos=(1200, 350)),
                       EnemyScooterboy(pos=(1400, 350)),
                       EnemyScooterboy(pos=(4800, 350)),
                       EnemyScooterboy(pos=(4800, 400)),
                       EnemyScooterboy(pos=(4900, 450))]),

        Stage(max_scroll_x=5500,
              enemies=[EnemyBoss(pos=(6500, 380)),
                       EnemyBoss(pos=(6500, 360))],
              weapons=[Barrel(pos=(6000, 400)),
                       Barrel(pos=(5900, 370))]),

        Stage(max_scroll_x=6400,
              enemies=[EnemyBoss(pos=(7000, 380)),
                       EnemyBoss(pos=(7000, 360)),
                       EnemyBoss(pos=(7000, 390))],
              weapons=[Barrel(pos=(7000, 380))]),

        Stage(max_scroll_x=6900,
              enemies=[EnemyScooterboy(pos=(7400, 400)),
                       EnemyScooterboy(pos=(7700, 400)),
                       EnemyScooterboy(pos=(8000, 400)),
                       EnemyScooterboy(pos=(8300, 400))],
              powerups=[ExtraLifePowerup(pos=(8600, config.MIN_WALK_Y))]),

        Stage(max_scroll_x=8800,
              enemies=[EnemyHoodie(pos=(9300, 380)),
                       EnemyHoodie(pos=(9300, 480)),
                       EnemyHoodie(pos=(10000, 380)),
                       EnemyHoodie(pos=(10000, 480)),
                       EnemyHoodie(pos=(11000, 380)),
                       EnemyHoodie(pos=(11000, 480))]),

        Stage(max_scroll_x=10000,
              enemies=[EnemyBoss(pos=(11000, 380)),
                       EnemyBoss(pos=(11000, 360)),
                       EnemyBoss(pos=(11000, 390)),
                       EnemyScooterboy(pos=(11000, 450))],
              weapons=[Barrel(pos=(11000, 350)),
                       Barrel(pos=(11000, 430)),
                       Barrel(pos=(11100, 390))]),

        Stage(max_scroll_x=11200,
              enemies=[EnemyVax(pos=(11500, 380)),
                       EnemyVax(pos=(11500, 400)),
                       EnemyVax(pos=(11500, 420)),
                       EnemyVax(pos=(11600, 380)),
                       EnemyVax(pos=(11600, 400)),
                       EnemyVax(pos=(11600, 420))]),

        Stage(max_scroll_x=13000,
              enemies=[EnemyHoodie(pos=(13300, 380)),
                       EnemyHoodie(pos=(13300, 420)),
                       EnemyHoodie(pos=(13300, 460)),
                       EnemyScooterboy(pos=(13300, 330)),
                       EnemyScooterboy(pos=(13300, 360)),
                       EnemyScooterboy(pos=(13300, 390)),
                       EnemyScooterboy(pos=(13300, 420))],
              powerups=[HealthPowerup(pos=(13200, config.MIN_WALK_Y))]),

        Stage(max_scroll_x=15000,
              enemies=[EnemyBoss(pos=(15600, 360)),
                       EnemyBoss(pos=(15600, 380)),
                       EnemyBoss(pos=(15600, 400)),
                       EnemyScooterboy(pos=(15600, 350)),
                       EnemyScooterboy(pos=(15600, 430))],
              weapons=[Barrel(pos=(15600, 350)),
                       Barrel(pos=(15600, 410)),
                       Barrel(pos=(15650, 390))]),

        Stage(max_scroll_x=17000,
              enemies=[EnemyVax(pos=(17400, 380)),
                       EnemyVax(pos=(17400, 420)),
                       EnemyVax(pos=(17500, 380)),
                       EnemyVax(pos=(17500, 420)),
                       EnemyVax(pos=(17700, 380)),
                       EnemyVax(pos=(17700, 420))]),

        Stage(max_scroll_x=19000,
              enemies=[EnemyHoodie(pos=(19500, 380)),
                       EnemyHoodie(pos=(19500, 420)),
                       EnemyScooterboy(pos=(19500, 350)),
                       EnemyScooterboy(pos=(19500, 390)),
                       EnemyScooterboy(pos=(19500, 430))],
              powerups=[ExtraLifePowerup(pos=(19500, config.MIN_WALK_Y))]),

        Stage(max_scroll_x=20500,
              enemies=[EnemyBoss(pos=(21500, 390)),
                       EnemyBoss(pos=(18200, 320)),
                       EnemyBoss(pos=(17800, 390)),
                       ],
              powerups=[ExtraLifePowerup(pos=(20900, config.MIN_WALK_Y))]),

        Stage(max_scroll_x=20500,
              enemies=[EnemyPortal(pos=(20700, 315), enemies=(EnemyVax,), start_timer=600, spawn_interval=60, spawn_interval_change=5, max_enemies=20),
                       EnemyPortal(pos=(20700, 440), enemies=(EnemyHoodie,), start_timer=600, spawn_interval=60, spawn_interval_change=10, max_enemies=20),
                       EnemyPortal(pos=(21100, 315), enemies=(EnemyScooterboy,), start_timer=600, spawn_interval=60, spawn_interval_change=15, max_enemies=20),
                       EnemyPortal(pos=(21100, 440), enemies=(EnemyBoss,), start_timer=600, spawn_interval=60, spawn_interval_change=20, max_enemies=20),
                       ]),
    )
