from abc import abstractmethod

from game.config import *
from game.actors.ScrollHeightActor import ScrollHeightActor


class Mask(ScrollHeightActor):
    def __init__(self, image, pos):
        super().__init__(pos, image)
        self.collected = False

    def update(self):
        pass

    @abstractmethod
    def collect(self, collector):
        self.collected = True