import pygame

from kelvin452.engine.fonts import default_font
from kelvin452.engine import *

level = 1


def add_level():
    global level
    level += 1


class LevelText(Entity):

    def __init__(self, x=60, y=28):
        super().__init__()
        global level
        level = 1
        self.position = Vector2(x, y)
        self.previous_level = 0
        self.survive_game_over = False
        self.text_sprite = KelvinSprite(pygame.Surface((0, 0)))
        self.text_sprite.layer = 300
        self.attach_component(self.text_sprite)

    def _tick(self):
        if self.previous_level != level:
            print(level)
            self.text_sprite.image = default_font.render(f"LEVEL : {level}",
                                                         True,
                                                         (255, 255, 255))
            self.text_sprite.dirty = 1
            self.previous_level = level
