import pygame
from kelvin452.engine import *

speed = 600 # pixels par secondes


class MovingFire(Entity):
    def __init__(self):
        super().__init__()
        self.position = Vector2(400, 400)
        scaled_sprite = pygame.transform.scale(assets.sprite("fire.png"), (220, 180))
        # Ne pas oublier self.attach_component pour associer le sprite à l'entité
        self.sprite = self.attach_component(KelvinSprite(scaled_sprite))

    def _tick(self):
        # Il faut pas oublier d'utiliser game.delta_time pour la concordance au temps sinon :
        # - avec 300 FPS le truc bouge super vite
        # - avec 30 FPS le truc bouge très lentement
        if game.input.is_key_down(pygame.K_RIGHT):
            self.position.x += speed * game.delta_time
        elif game.input.is_key_down(pygame.K_LEFT):
            self.position.x -= speed * game.delta_time

        if game.input.is_key_down(pygame.K_UP):
            self.position.y -= speed * game.delta_time
        elif game.input.is_key_down(pygame.K_DOWN):
            self.position.y += speed * game.delta_time


def game_start():
    game.world.spawn_entity(MovingFire())


def launch_game():
    game.initialize_game()
    game.on_start(game_start)
    game.start()


if __name__ == "__main__":
    launch_game()
