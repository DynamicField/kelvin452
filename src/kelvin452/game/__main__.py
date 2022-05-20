import pygame.transform

from kelvin452.engine import *
import random


class FireEntity(Entity, ReactsToCollisions):
    def __init__(self, x, y, control=False):
        super().__init__()
        self.control = control
        self.position = Vector2(x, y)
        huge_fire_sprite = pygame.transform.scale(assets.sprite("fire.png"), (220, 180))
        self.__sprite = self.attach_component(KelvinSprite(huge_fire_sprite))
        self.__collision = self.attach_component(CollisionHitBox(follow_sprite_rect=True, draw_box=True))

    def _on_collide(self, other: Entity):
        print("oskour la collision vers " + str(other))

    def _tick(self):
        if self.control:
            self.position = pygame.mouse.get_pos()
        else:
            self.position.x = ((self.position.x + 500 * game.delta_time) % game.viewport.x)
            self.position.y = ((self.position.y + 50 * game.delta_time) % game.viewport.y)


def game_start():
    for i in range(2):
        game.world.spawn_entity(FireEntity(random.randint(0, 1000), random.randint(200, 750)))
    game.world.spawn_entity(FireEntity(1000, 720, control=True))


def launch_game():
    game.initialize_game()
    game.on_start(game_start)
    game.start()


if __name__ == "__main__":
    launch_game()
