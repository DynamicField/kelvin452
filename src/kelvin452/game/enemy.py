import pygame
from kelvin452.engine.fonts import default_font
from kelvin452.engine import *

enemy = 0


def add_enemy(value):
    global enemy
    enemy += value


class EnemyText(Entity):
    def __init__(self, x=1161, y=612):
        super().__init__()
        self.position = Vector2(x, y)
        self.previous_enemy = -1
        self.survive_game_over = False
        self.text_sprite = KelvinSprite(pygame.Surface((self.position.x, self.position.y)))
        self.text_sprite.layer = 300
        self.attach_component(self.text_sprite)

    def _tick(self):
        # Refaire le rendu du texte uniquement lorsque le enemy change
        if self.previous_enemy != enemy:
            self.text_sprite.image = default_font.render(f"ENEMY : {enemy}",
                                                         True,
                                                         (255, 255, 255))
            self.text_sprite.dirty = 1  # Mettre à jour le sprite
            self.previous_enemy = enemy
