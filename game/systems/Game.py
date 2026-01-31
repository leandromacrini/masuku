from random import choice, randint

from pygame import Vector2, Rect
import pygame

from pgzero.builtins import images, sounds, music

from game.config import *
from game.utils import Profiler, move_towards
import game.stages.setup_stages as stage_setup
from game.ui.text import draw_text, draw_text_otf, font_mikachan, font_mikachan_big
import game.runtime as runtime
from game.entities.Player import Player
from game.stages.Stage import BossStage

from game.entities.Enemy import Enemy

fullscreen_black_bmp = pygame.Surface((WIDTH, HEIGHT))
fullscreen_black_bmp.fill((0, 0, 0))


class Game:
    def __init__(self, controls=None):
        self.player = Player(controls)

        self.enemies = []
        self.weapons = []
        self.scooters = []
        self.powerups = []

        self.stage_index = -1
        self.timer = 0
        self.score = 0

        self.scroll_offset = Vector2(0,0)
        self.max_scroll_offset_x = 0
        self.scrolling = False

        self.boundary = Rect(0, MIN_WALK_Y, WIDTH-1, HEIGHT-MIN_WALK_Y)

        stage_setup.setup_stages()

        # Set up intro text, selecting randomly from one of several stolen items
        stolen_items = ("A SHIPMENT OF RASPBERRY\nPIS",
                        "YOUR COPY OF CODE THE\nCLASSICS VOL 2",
                        "THE COMPLETE WORKS OF\nSHAKESPEARE",
                        "THE BLOCKCHAIN",
                        "THE WORLD'S ENTIRE SUPPLY\nOF COVID VACCINES",
                        "ALL OF YOUR SAVED GAME\nFILES",
                        "YOUR DOG'S FLEA MEDICINE")

        self.text_active = INTRO_ENABLED
        self.intro_text = "THE NOTORIOUS CRIME BOSS\nEBEN UPTON HAS STOLEN\n" \
                          + choice(stolen_items) \
                          + "\n\n\nFIGHT TO RECLAIM WHAT\nHAS BEEN TAKEN!"
        self.outro_text = "FOLLOWING THE DEFEAT OF\n" \
                          + "THE EVIL GANG, HUMANITY\n" \
                          + "ENTERED A NEW GOLDEN AGE\n" \
                          + "IN WHICH CRIME BECAME A\n" \
                          + "THING OF THE PAST. THE\n" \
                          + "WORD ITSELF WAS SOON\n" \
                          + "FORGOTTEN AND EVERYONE\n" \
                          + "HAD A BIG PARTY IN YOUR\n" \
                          + "HONOUR.\n" \
                          + "\nNICE JOB!"
        self.current_text = self.intro_text
        self.displayed_text = ""

        self.boss_intro_active = False
        self.boss_intro_phase = None
        self.boss_intro_timer = 0
        self.boss_intro_boss = None
        self.boss_intro_target_x = None
        self.boss_intro_stage = None
        self.boss_intro_scroll_target_x = None
        self.boss_intro_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.boss_intro_scroll_start_x = None
        self.boss_intro_boss_start_x = None
        self.boss_intro_boss_target_x = None

    def next_stage(self):
        # A stage is over when we've scrolled to its max_scroll_x and there are no enemies left
        # Enemies are created when we start scrolling (or here, if no scrolling is to take place or is already taking place)
        
        self.stage_index += 1
        if self.stage_index < len(stage_setup.STAGES):
            stage = stage_setup.STAGES[self.stage_index]
            if stage.music_track is not None:
                music.play(stage.music_track)
            self.max_scroll_offset_x = stage.max_scroll_x
            weather = runtime.get_weather()
            if weather is not None:
                weather.set_weather(stage.weather)
            if self.scrolling or self.max_scroll_offset_x <= self.scroll_offset.x:
                print("No scrolling or already scrolling - create stage objects")
                self.create_stage_objects(stage)
        else:
            weather = runtime.get_weather()
            if weather is not None:
                weather.stop()
            # If stage_index has reached len(STAGES), we go into the outro state (like intro text, but with different text)
            # After that, check_won() will return True and the game state code will pick up on this and end the game
            if not self.text_active:
                self.text_active = True
                self.current_text = self.outro_text
                self.displayed_text = ""
                self.timer = 0

    def check_won(self):
        # Have we been through all stages, and has the outro text finished?
        return self.stage_index >= len(stage_setup.STAGES) and not self.text_active

    def create_stage_objects(self, stage):
        # Copy the enemies list from the stage, and tell them that they've been spawned
        self.enemies = stage.enemies.copy()
        for enemy in self.enemies:
            enemy.spawned()

        # Add the weapons and powerups from the stage to the game
        self.weapons.extend(stage.weapons)
        self.powerups.extend(stage.powerups)

        if isinstance(stage, BossStage):
            # Keep boss offscreen and paused until intro starts
            boss = stage.boss
            boss.state = Enemy.State.IDLE
            boss.state_timer = 0
            boss.vpos.x = stage.max_scroll_x + WIDTH + 200
            boss.target = boss.vpos.copy()

        # Boss intro is triggered later (after scroll/player position), see update()

    def spawn_enemy(self, enemy):
        # Called by Portal
        self.enemies.append(enemy)
        enemy.spawned()

    def update(self):
        if DEBUG_PROFILING:
            p = Profiler()

        self.timer += 1
        weather = runtime.get_weather()
        if weather is not None:
            weather.update()

        if self.text_active:
            # Every 6 frames, update the displayed text to display an extra character, and make a sound if the
            # new character is visible (as opposed to a space or new line)
            if self.timer % 6 == 0 and len(self.displayed_text) < len(self.current_text):
                length_to_display = min(self.timer // 6, len(self.current_text))
                self.displayed_text = self.current_text[:length_to_display]
                if not self.displayed_text[-1].isspace():
                    self.play_sound("sfx/ui/teletype")

            # Allow player to skip/leave text
            for button in range(4):
                if self.player.controls.button_pressed(button):
                    self.text_active = False
                    self.timer = 0

            return

        if self.boss_intro_active:
            self.update_boss_intro()
            return

        if DEBUG_SHOW_ATTACKS:
            runtime.debug_drawcalls.clear()

        # Update all objects
        for obj in [self.player] + self.enemies + self.weapons + self.scooters + self.powerups:
            obj.update()

        if self.scrolling:
            if self.scroll_offset.x < self.max_scroll_offset_x:
                # How far are we from reaching the new max scroll offset?
                diff = self.max_scroll_offset_x - self.scroll_offset.x
                # Scroll at 1-4px per frame depending on player's distance from right edge
                scroll_speed = self.player.x / (WIDTH/4)
                scroll_speed = min(diff, scroll_speed)
                self.scroll_offset.x += scroll_speed
                self.boundary.left = self.scroll_offset.x  # as boundary is a rectangle, moving boundary.left moves the entire rectangle
            else:
                # Scrolling is complete
                self.scrolling = False
                # Trigger boss intro only after scroll finishes and player is near the right side
                if self.stage_index < len(stage_setup.STAGES):
                    stage = stage_setup.STAGES[self.stage_index]
                    if isinstance(stage, BossStage) and not stage.intro_played:
                        if self.player.vpos.x - self.scroll_offset.x >= WIDTH/3:
                            self.prepare_boss_intro(stage)
                            stage.intro_played = True
        else:
            # Start scrolling if player is near right hand edge of screen and max_scroll_offset_x allows to to scroll
            begin_scroll_boundary = WIDTH - 300
            if self.player.vpos.x - self.scroll_offset.x > begin_scroll_boundary and self.scroll_offset.x < self.max_scroll_offset_x:
                self.scrolling = True

                # When we start scrolling, create enemies for the current stage
                if self.stage_index < len(stage_setup.STAGES):
                    print("Started scrolling - create stage objects")
                    stage = stage_setup.STAGES[self.stage_index]
                    self.create_stage_objects(stage)
            else:
                # Earlier scroll trigger for boss stages
                if self.stage_index < len(stage_setup.STAGES):
                    stage = stage_setup.STAGES[self.stage_index]
                    if isinstance(stage, BossStage):
                        boss_scroll_boundary = WIDTH - 450
                        if self.player.vpos.x - self.scroll_offset.x > boss_scroll_boundary and self.scroll_offset.x < self.max_scroll_offset_x:
                            self.scrolling = True
                            print("Started scrolling (boss stage) - create stage objects")
                            self.create_stage_objects(stage)

        # Fallback trigger if scroll is already finished (or never started)
        if self.stage_index < len(stage_setup.STAGES):
            stage = stage_setup.STAGES[self.stage_index]
            if isinstance(stage, BossStage) and not stage.intro_played and not self.boss_intro_active:
                if self.scroll_offset.x >= self.max_scroll_offset_x:
                    if self.player.vpos.x - self.scroll_offset.x >= WIDTH - 260:
                        self.prepare_boss_intro(stage)
                        stage.intro_played = True

        # Remove expired enemies and gain score
        self.score += sum([enemy.score for enemy in self.enemies if enemy.lives <= 0])
        self.enemies = [enemy for enemy in self.enemies if not enemy.should_remove()]

        # Remove expired scooters
        self.scooters = [scooter for scooter in self.scooters if scooter.frame < 200]

        # Remove broken weapons and ones which are off the left of the screen
        self.weapons = [weapon for weapon in self.weapons if not weapon.is_broken() and weapon.x > -200]

        # Remove collected powerups, and ones off the left of the screen
        self.powerups = [powerup for powerup in self.powerups if not powerup.collected and powerup.x > -200]

        # If no enemies and we've fully scrolled to the current stage's max_scroll_x, start the next stage
        if len(self.enemies) == 0 and self.scroll_offset.x == self.max_scroll_offset_x:
            self.next_stage()

        if DEBUG_PROFILING:
            print(f"update: {p.get_ms()}")

    def draw(self, screen):
        # Draw background
        self.draw_background(screen)

        # Draw all objects, lowest on screen first
        # Y pos used is modified by result of get_draw_order_offset, for certain cases where we need more nuance than
        # just "lowest on screen first"
        p = Profiler()
        all_objs = [self.player] + self.enemies + self.weapons + self.scooters + self.powerups
        all_objs.sort(key=lambda obj: obj.vpos.y + obj.get_draw_order_offset())
        for obj in all_objs:
            if obj:
                obj.draw(self.scroll_offset)
        if DEBUG_PROFILING:
            print("objs: {0}".format(p.get_ms()))

        p = Profiler()
        weather = runtime.get_weather()
        if weather is not None:
            weather.draw(screen)

        # If player can scroll the level, show flashing arrow
        if self.scroll_offset.x < self.max_scroll_offset_x and (self.timer // 30) % 2 == 0:
            screen.blit("ui/arrow", (WIDTH-450, 120))

        self.draw_ui(screen)

        self.draw_ui_boss(screen)

        if DEBUG_PROFILING:
            print("icons: {0}".format(p.get_ms()))
            p = Profiler()

        # During the intro we show a black background, immediately after the intro we fade it away
        # Draw a black image with gradually decreasing opacity
        # An alpha value of 255 is fully opaque, 0 is fully transparent
        if self.text_active or self.timer < 255:
            if self.text_active:
                alpha = 255
            else:
                alpha = max(0, 255 - self.timer)
            fullscreen_black_bmp.set_alpha(alpha)
            screen.blit(fullscreen_black_bmp, (0, 0))

        # Show intro text
        if self.text_active:
            draw_text(screen, self.displayed_text, 50, 50)

        if self.boss_intro_active and self.boss_intro_phase == "title":
            self.draw_boss_intro(screen)

        # Debug
        if DEBUG_SHOW_SCROLL_POS:
            screen.draw.text(f"{self.scroll_offset} {self.max_scroll_offset_x}", (0, 25))
            screen.draw.text(str(self.boundary.left), (0, 45))

        if DEBUG_SHOW_BOUNDARY:
            screen.draw.rect(Rect(self.boundary.left - self.scroll_offset.x, self.boundary.top, self.boundary.width, self.boundary.height), (255,255,255))

        # If there are any debug draw calls, execute them - used by DEBUG_SHOW_ATTACKS
        for func in runtime.debug_drawcalls:
            func()

        if DEBUG_PROFILING:
            # Show profiler timing for everything not in another category
            print("rest: {0}".format(p.get_ms()))

    def draw_ui(self, screen):
        # Show status bar and player health, stamina and lives
        # Have to use the actual Pygame blit rather than Pygame Zero version so that we can specify which area of the
        # source image to copy
        health_bar_w = int((self.player.health / self.player.start_health) * HEALTH_STAMINA_BAR_WIDTH)
        screen.surface.blit(images.load("ui/health"), (48, 11), Rect(0, 0, health_bar_w, HEALTH_STAMINA_BAR_HEIGHT))
        stamina_bar_w = int((self.player.stamina / self.player.max_stamina) * HEALTH_STAMINA_BAR_WIDTH)
        screen.surface.blit(images.load("ui/stamina"), (517, 11), Rect(0, 0, stamina_bar_w, HEALTH_STAMINA_BAR_HEIGHT))

        screen.blit("ui/status", (0, 0))

        for i in range(self.player.lives):
            if self.player.extra_life_timer <= 0 or i < self.player.lives - 1:
                sprite_idx = 9
            else:
                sprite_idx = min(9, (30 - self.player.extra_life_timer) // 3)

            screen.blit(f"ui/status_life{sprite_idx}", (i * 46 - 55, -35))

        # Show score
        draw_text(screen, f"{self.score:04}", WIDTH // 2, 0, True)


    def draw_ui_boss(self,screen):
        for enemy in self.enemies:
            if enemy.enemy_type in [Enemy.EnemyType.MID_BOSS, Enemy.EnemyType.FINAL_BOSS] and not self.boss_intro_active and self.boss_intro_phase is None and enemy.state != Enemy.State.IDLE:
                draw_text_otf(screen, enemy.title_name, BOSS_NAME_X_POS + 1, BOSS_NAME_Y_POS + 1, font_mikachan, BOSS_COLOR_SHADOW, True )
                draw_text_otf(screen, enemy.title_name, BOSS_NAME_X_POS, BOSS_NAME_Y_POS, font_mikachan, BOSS_COLOR_RED, True)
                health_bar_w = int((enemy.health / enemy.start_health) * BOSS_HEALTH_STAMINA_BAR_WIDTH)
                screen.surface.blit(images.load("ui/health_boss"), (BOSS_HEALTH_BAR_X_POS, BOSS_HEALTH_BAR_Y_POS), Rect(0, 0, health_bar_w, BOSS_HEALTH_STAMINA_BAR_HEIGHT))

    def prepare_boss_intro(self, stage):
        self.boss_intro_active = True
        self.boss_intro_phase = "scroll"
        self.boss_intro_timer = 0
        self.boss_intro_stage = stage
        self.boss_intro_boss = stage.boss
        # Snapshot deterministic targets
        self.boss_intro_scroll_start_x = self.scroll_offset.x
        self.boss_intro_scroll_target_x = stage.max_scroll_x
        self.boss_intro_boss_target_x = self.scroll_offset.x + WIDTH - 220
        self.boss_intro_boss_start_x = self.scroll_offset.x + WIDTH + 220
        stage.boss.vpos.x = self.boss_intro_boss_start_x
        stage.boss.target = stage.boss.vpos.copy()
        stage.boss.facing_x = -1
        stage.boss.walking = True

    def update_boss_intro(self):
        if self.boss_intro_boss is None or self.boss_intro_stage is None:
            self.boss_intro_active = False
            return

        boss = self.boss_intro_boss
        stage = self.boss_intro_stage

        if self.boss_intro_phase == "scroll":
            # Finish scroll before boss enters (deterministic target)
            if self.scroll_offset.x < self.boss_intro_scroll_target_x:
                diff = self.boss_intro_scroll_target_x - self.scroll_offset.x
                scroll_speed = max(2.0, min(diff, 6.0))
                self.scroll_offset.x += scroll_speed
                self.boundary.left = self.scroll_offset.x
            if self.scroll_offset.x >= self.boss_intro_scroll_target_x:
                self.boss_intro_phase = "walk"
        elif self.boss_intro_phase == "walk":
            boss.walking = True
            boss.frame += 1
            boss.vpos.x, _ = move_towards(boss.vpos.x, self.boss_intro_boss_target_x, stage.intro_walk_speed)
            if boss.vpos.x == self.boss_intro_boss_target_x:
                boss.walking = False
                boss.frame = 0
                self.boss_intro_phase = "title"
                self.boss_intro_timer = 0
        elif self.boss_intro_phase == "title":
            self.boss_intro_timer += 1
            if self.boss_intro_timer >= stage.intro_hold_frames:
                self.boss_intro_active = False
                self.boss_intro_phase = None
                self.boss_intro_timer = 0
                # Release boss AI after intro
                boss.state = Enemy.State.APPROACH_PLAYER
                boss.state_timer = 0
                if hasattr(boss, "make_decision"):
                    boss.make_decision()

    def draw_boss_intro(self, screen):
        if self.boss_intro_boss is None or self.boss_intro_stage is None:
            return

        stage = self.boss_intro_stage
        boss = self.boss_intro_boss

        self.boss_intro_overlay.fill((0, 0, 0, stage.intro_overlay_alpha))
        screen.surface.blit(self.boss_intro_overlay, (0, 0))

        intro_image_name = getattr(boss, "boss_intro_image", None)
        if intro_image_name:
            sprite_dir = SPRITE_DIRS.get(boss.sprite, "")
            if sprite_dir:
                intro_image_name = f"{sprite_dir}/{intro_image_name}"
            boss_image = images.load(intro_image_name)
            screen.blit(boss_image, (WIDTH // 2 - boss_image.get_width() // 2, HEIGHT // 2 - boss_image.get_height() // 2))

        title = getattr(boss, "title_name", "BOSS")
        draw_text_otf(screen, title, WIDTH // 2 - 198, HEIGHT - 78, font_mikachan_big, (0,0,0))
        draw_text_otf(screen, title, WIDTH // 2 - 200, HEIGHT - 80, font_mikachan_big, (255,255,255))


    def draw_background(self, screen):
        # Draw two copies of road background
        p = Profiler()
        road1_x = -(self.scroll_offset.x % WIDTH)
        road2_x = road1_x + WIDTH
        screen.blit("backgrounds/road", (road1_x, 0))
        screen.blit("backgrounds/road", (road2_x, 0))
        if DEBUG_PROFILING:
            print("road " + str(p.get_ms()))

        # Set initial position for background tiles
        # Due to isometric nature of background, each background tile includes a transparent part - the second line
        # skips that part for the first tile
        pos = -self.scroll_offset
        pos.x -= BACKGROUND_TILE_SPACING

        # Draw background tiles
        p = Profiler()
        for tile in BACKGROUND_TILES:
            # Don't bother drawing tile if it's off the left of the screen
            if pos.x + 417 >= 0:
                screen.blit(tile, pos)
                pos.x += BACKGROUND_TILE_SPACING
                if pos.x >= WIDTH:
                    # Stop once we've reached or gone past the right edge of the screen
                    break
            else:
                pos.x += BACKGROUND_TILE_SPACING
        if DEBUG_PROFILING:
            print("bg " + str(p.get_ms()))

    def shutdown(self):
        # When game is over, we need to tell enemies to die, since that's how the scooter engine sound effect gets
        # turned off
        for enemy in self.enemies:
            enemy.died()

    def get_sound(self, name, count=1):
        if self.player:
            return sounds.load(f"{name}{randint(0, count - 1)}")

    def play_sound(self, name, count=1):
        # Some sounds have multiple varieties. If count > 1, we'll randomly choose one from those
        # We don't play any sounds if there is no player (e.g. if we're on the menu)
        if self.player:
            try:
                # Pygame Zero allows you to write things like 'sounds.explosion.play()'
                # This automatically loads and plays a file named 'explosion.wav' (or .ogg) from the sounds folder (if
                # such a file exists)
                # But what if you have files named 'explosion0.ogg' to 'explosion5.ogg' and want to randomly choose
                # one of them to play? You can generate a string such as 'explosion3', but to use such a string
                # to access an attribute of Pygame Zero's sounds object, we must use Python's built-in function getattr
                sound = self.get_sound(name, count)
                sound.play()
            except Exception as e:
                # If no sound file of that name was found, print the error that Pygame Zero provides, which
                # includes the filename.
                # Also occurs if sound fails to play for another reason (e.g. if this machine has no sound hardware)
                print(e)

# From Eggzy
