from systems.rendering import make_sprite
from systems.world import Entity
from game import game
from assets import all_assets
import random


class FireEntity(Entity):
    def __init__(self, x, y):
        super().__init__()
        self.__x = x
        self.__y = y
        self.__sprite = make_sprite(all_assets.fire_sprite, (x, y))

    def _spawned(self):
        self.show_sprite(self.__sprite)

    def _tick(self):
        self.__x += 454.5 * game.delta_time
        self.__y += 40.0 * game.delta_time
        if self.__x > game.viewport[0]:
            self.__x = 0
        if self.__y > game.viewport[1]:
            self.__y = 0
        self.__sprite.rect.topleft = self.__x, self.__y
        self.__sprite.dirty = 1


def game_start():
    for i in range(100):
        fire_entity = FireEntity(random.randint(0, 1280), random.randint(0, 720))
        game.world.spawn_entity(fire_entity)


def main():
    game.initialize_game()
    game.on_start(game_start)
    game.start()


if __name__ == "__main__":
    main()
