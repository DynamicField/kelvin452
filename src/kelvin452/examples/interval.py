import random

import pygame
from kelvin452.engine import *

duration = 0.1


class Spawner(Entity):
    def __init__(self):
        super().__init__()
        self.timer = duration

    def _tick(self):
        # game.delta_time donne le temps passé entre la frame d'avant et la frame maintenant.
        self.timer -= game.delta_time
        if self.timer < 0:
            game.world.spawn_entity(MadFire())
            self.timer = duration  # On reset le timer


class MadFire(Entity):
    def __init__(self):
        super().__init__()
        self.position = Vector2(0, random.randint(0, 520))
        self.fire_image = pygame.transform.scale(assets.sprite("fire.png"), (220, 180))
        self.sprite = self.attach_component(KelvinSprite(self.fire_image, auto_update=False))
        self.angle = 0

    def _tick(self):
        self.position.x += 500 * game.delta_time
        if self.position.x > game.viewport.x:
            self.destroy()
            return

        self.angle += 180 * game.delta_time

        self.sprite.position = self.position
        self.sprite.image = pygame.transform.rotate(self.fire_image, self.angle)
        # On recentre l'image à cause de la rotation
        self.sprite.rect = self.sprite.image.get_rect(center=self.position)

    def _destroyed(self):
        print("Décès du feu en COLÈREEEEE")


def game_start():
    game.world.spawn_entity(Spawner())


def launch_game():
    game.initialize_game()
    game.on_start(game_start)
    game.start()


if __name__ == "__main__":
    launch_game()
