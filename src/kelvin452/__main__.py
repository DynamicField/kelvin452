import pygame.transform
from pygame import Rect

from kelvin452.engine import *

import random


class Piece1Entity(Entity):
    def __init__(self, x, y):
        super().__init__()
        self.position = Vector2(x, y)

        a = random.randint(32, 64)
        p1ed = pygame.transform.scale(assets.sprite("p1ed.png"), (a, a))
        self.__sprite = self.attach_component(make_sprite(p1ed, (x, y)))
        self.p1ed_rect = self.__sprite.rect

    def _tick(self):
        self.position.x += 200 * game.delta_time
        if self.position.x > 1000:
            self.position.x = 1000
        """if self.p1ed_rect.colliderect(Rect(1000,0,100,900)):
            game.world.destroy_entity(self)"""


class Entity_spawn(Entity):
    def __init__(self):
        super().__init__()
        self.compteurino = 10
        self.compteuridos = 0.4
        self.compte2 = False

    def _tick(self):
        self.compteur(10)
        if self.compte2 == True:
            self.compteur2(0.4)

    def compteur(self, temps):
        z = 0
        b = [120, 190, 260, 330, 400]
        self.compteurino -= game.delta_time
        if self.compteurino <= 0:
            self.compte2 = True
            for i in range(5):
                if z >= 5:
                    z = 0
                p1ed_entity = Piece1Entity(0, b[z])
                game.world.spawn_entity(p1ed_entity)
                z += 1
            self.compteurino = temps

    def compteur2(self, temps):
        z = 0
        b = [120, 190, 260, 330, 400]
        p10ed_number = random.randint(1, 5)
        self.compteuridos -= game.delta_time
        if self.compteuridos <= 0:
            for i in range(p10ed_number):
                if z >= 5:
                    z = 0
                p10ed_entity = Piece10Entity(0, b[z])
                game.world.spawn_entity(p10ed_entity)
                z += 1
            self.compteuridos = temps
            self.compte2 = False


class Piece10Entity(Entity):
    def __init__(self, x, y):
        super().__init__()
        self.position.x = x
        self.position.y = y
        a = random.randint(32, 64)
        p10ed = pygame.transform.scale(assets.sprite("p10ed.png"), (a, a))
        self.__sprite = self.attach_component(make_sprite(p10ed, (x, y)))
        self.p10ed_rect = self.__sprite.rect

    def _tick(self):
        self.position.x += 200 * game.delta_time
        if self.position.x > game.viewport[0] - 700:
            self.position.x = game.viewport[0] - 700


class ProjEntity(Entity):
    def __init__(self, x, y):
        super().__init__()
        self.position.x = x
        self.position.y = y


def game_start():
    z = 0
    b = [120, 190, 260, 330, 400]
    spawner = Entity_spawn()
    game.world.spawn_entity(spawner)
    for i in range(5):
        if z >= 5:
            z = 0
        p1ed_entity = Piece1Entity(0, b[z])
        game.world.spawn_entity(p1ed_entity)
        z += 1


def launch_game():
    game.initialize_game()
    game.on_start(game_start)
    game.start()


if __name__ == "__main__":
    launch_game()
