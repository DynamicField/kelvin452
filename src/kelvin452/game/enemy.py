import pygame
from kelvin452.engine.fonts import default_font
from kelvin452.engine import *

enemy = 100000000000
max_enemies_on_screen = 100


def basic_enemy(value):
    modify_enemy(value - enemy)


def modify_enemy(amount):
    import kelvin452.game.__main__ as main
    import random

    global enemy
    if amount < -enemy:  # Prevent negative values
        amount = -enemy
    enemy += amount

    if amount > 0:
        displayed_enemies = len(game.world.get_entities(main.EnemyEntity))
        for _ in range(amount):
            if displayed_enemies > max_enemies_on_screen:
                random_enemy = random.choice(game.world.get_entities(main.EnemyEntity))
                game.world.destroy_entity(random_enemy)
            else:
                displayed_enemies += 1

            enemy_entity = main.EnemyEntity()
            game.world.spawn_entity(enemy_entity)
    elif amount < 0:
        for _ in range(-amount):
            enemies = game.world.get_entities(main.EnemyEntity)
            if len(enemies) == 0:
                break
            game.world.destroy_entity(enemies[0])


class EnemyText(Entity):
    def __init__(self, x=1161, y=612):
        super().__init__()
        basic_enemy(enemy)
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
