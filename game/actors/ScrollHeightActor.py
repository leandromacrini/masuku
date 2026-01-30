from pgzero.builtins import Actor
from pygame import Vector2

from game import config


# The ScrollHeightActor class extends Pygame Zero's Actor class by providing the attribute 'vpos', which stores the
# object's current position using Pygame's Vector2 class. All code should change or read the position via vpos, as
# opposed to Actor's x/y or pos attributes. When the object is drawn, we set self.pos (equivalent to setting both
# self.x and self.y) based on vpos, but taking scrolling into account.
# It also includes the attribute height_above_ground which allows an actor to be considered to be in the air. This
# should be taken into account when determining draw order, as a fighter who is jumping will be further up the screen
# on the Y axis than if they were on the ground, but it's their Y position in relation to the ground which should
# determine whether they're drawn behind or in front of other actors.
class ScrollHeightActor(Actor):
    def __init__(self, img, pos, anchor=None, separate_shadow=False):
        super().__init__(img, pos, anchor=anchor)
        self.vpos = Vector2(pos)
        self.height_above_ground = 0
        if separate_shadow:
            self.shadow_actor = Actor(config.BLANK_IMAGE, pos, anchor=anchor)
        else:
            self.shadow_actor = None

    # We draw with the supplied Vector2 offset to enable scrolling
    def draw(self, offset):
        # Draw shadow first, if we are using a separate shadow sprite (most have the shadow as part of the sprite
        # but for player it is separate)
        if self.shadow_actor is not None:
            self.shadow_actor.pos = (self.vpos.x - offset.x, self.vpos.y - offset.y)
            self.shadow_actor.image = config.BLANK_IMAGE if self.image == config.BLANK_IMAGE else self.image + "_shadow"
            self.shadow_actor.draw()

        # Set Actor's screen pos
        self.pos = (self.vpos.x - offset.x, self.vpos.y - offset.y - self.height_above_ground)
        super().draw()
        if config.DEBUG_SHOW_ANCHOR_POINTS:
            screen.draw.circle(self.pos, 5, (255, 255, 255))

    def on_screen(self):
        # Use self.x rather than self.vpos.x to get actual screen position rather than world position
        # Note that self.x only updates when the actor is drawn, so if vpos.x is updated during update causing the
        # actor to move off-screen, the value returned by this method will not update until the following frame
        return 0 < self.x < config.WIDTH

    def get_draw_order_offset(self):
        # See Player and Stick classes for explanation
        return 0
