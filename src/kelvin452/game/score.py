import pygame

from kelvin452.engine.fonts import default_font
from kelvin452.engine import *

score = 0


def basic_score(value):
    global score
    score = value


def add_score(value):
    global score
    score += value


class ScoreText(Entity):
    def __init__(self, y=670):
        super().__init__()
        self.position.y = y
        self.previous_score = -1
        self.survive_game_over = True
        self.text_sprite = KelvinSprite(pygame.Surface((0, 0)))
        self.text_sprite.layer = 200
        self.attach_component(self.text_sprite)

    def _tick(self):
        # Refaire le rendu du texte uniquement lorsque le score change
        if self.previous_score != score:
            self.text_sprite.image = default_font.render(f"SCORE : {score}",
                                                         True,
                                                         (255, 255, 255))
            # Centrer le score
            self.position.x = (game.viewport.x - self.text_sprite.image.get_rect().width) / 2
            self.text_sprite.dirty = 1  # Mettre à jour le sprite
            self.previous_score = score
