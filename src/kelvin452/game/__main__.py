import pygame.transform

from kelvin452.engine.systems.rendering import make_sprite
from kelvin452.engine.systems.world import Entity
from kelvin452.engine.game import game
from kelvin452.engine.assets import all_assets
import random


class FireEntity(Entity):
    def __init__(self, x, y):
        super().__init__()
        self.__x = x
        self.__y = y
        self.position = [x, y]
        huge_fire_sprite = pygame.transform.scale(all_assets.sprite("fire.png"), (90, 90))
        self.__sprite = make_sprite(huge_fire_sprite, (x, y))

    def add_y(self, add):  # add is the value we add in position y value, for example y == 10, add_y(10) put y at 20
        self.__y += add

    def _spawned(self):
        self.show_sprite(self.__sprite)

    def _tick(self):
        if game.input.is_key_down(pygame.K_DOWN):
            if self.__y + 100 <= 720:
                self.add_y(10)
        if game.input.is_key_down(pygame.K_UP):
            if self.__y - 10 >= 0:
                self.add_y(-10)
        self.__sprite.rect.topleft = self.__x, self.__y  # type: ignore
        self.__sprite.dirty = 1
        self.position[0] = self.__x
        self.position[1] = self.__y

    def get_position(self):
        return self.position


def game_start():
    fire_entity = FireEntity(1024, 315)
    game.world.spawn_entity(fire_entity)


def launch_game():
    game.initialize_game()
    game.on_start(game_start)
    game.start()


if __name__ == "__main__":
    launch_game()
