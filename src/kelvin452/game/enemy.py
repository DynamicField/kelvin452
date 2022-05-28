import pygame
from kelvin452.engine.fonts import default_font
from kelvin452.engine import *

enemy = 0


def add_enemy(value):
    global enemy
    enemy += value


class EnemyText(Entity):
    def __init__(self, x=900, y=640):
        super().__init__()
        self.position = Vector2(x, y)
        self.previous_enemy = -1
        self.survive_game_over = True
        self.text_sprite = self.attach_component(KelvinSprite(pygame.Surface((0, y))))

    def _tick(self):
        # Refaire le rendu du texte uniquement lorsque le enemy change
        if self.previous_enemy != enemy:
            self.text_sprite.image = default_font.render(f"ENEMY : {enemy}",
                                                         True,
                                                         (255, 255, 255))
            # Centrer le enemy
            self.position.x = (game.viewport.x - self.text_sprite.image.get_rect().width) / 2
            self.text_sprite.dirty = 1  # Mettre à jour le sprite
            self.previous_enemy = enemy
