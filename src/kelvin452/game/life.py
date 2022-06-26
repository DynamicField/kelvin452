import pygame

from kelvin452.engine.fonts import default_font
from kelvin452.engine import *
from kelvin452.game.__main__ import end_game

life = 1


def basic_life(value):
    global life
    life = value


def modify_life(amount):
    global life
    life += amount
    if life <= 0:
        end_game()


class LifeText(Entity):

    def __init__(self, x=1161, y=28):
        super().__init__()
        basic_life(1)
        self.position = Vector2(x, y)
        self.previous_life = 0
        self.survive_game_over = False
        self.text_sprite = KelvinSprite(pygame.Surface((0, 0)))
        self.text_sprite.layer = 300
        self.attach_component(self.text_sprite)

    def _tick(self):
        global life
        if life == 0:
            end_game()
        if self.previous_life != life:
            self.text_sprite.image = default_font.render(f"LIFE : {life}", True, (255, 0, 0))

            self.text_sprite.dirty = 1
            self.previous_life = life
