import pygame

from kelvin452.engine.fonts import default_font
from kelvin452.engine import *


class Foreground(Entity):
    def __init__(self):
        super().__init__()
        self.foreground = KelvinSprite(assets.grounds("foreground.png"))
        self.foreground.layer = 200
        self.attach_component(self.foreground)


class Objects(Entity):
    def __init__(self):
        super().__init__()
        self.objects = KelvinSprite(assets.grounds("objects.png"))
        self.objects.layer = 100
        self.attach_component(self.objects)
