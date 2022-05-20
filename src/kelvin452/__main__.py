import pygame.transform
from pygame import Rect

from kelvin452.systems.rendering import make_sprite
from kelvin452.systems.world import Entity
from kelvin452.game import game
from kelvin452.assets import all_assets
import random


class FireEntity(Entity):
    def __init__(self, x, y):
        super().__init__()
        self.__x = x
        self.__y = y
        huge_fire_sprite = pygame.transform.scale(all_assets.fire_sprite, (220, 180))
        self.__sprite = make_sprite(huge_fire_sprite, (x, y))

    def _spawned(self):
        self.show_sprite(self.__sprite)

    def _tick(self):
        self.__x += 500 * game.delta_time
        self.__y += 50 * game.delta_time
        if self.__x > game.viewport[0]:
            self.__x = 0
        if self.__y > game.viewport[1]:
            self.__y = 0
        self.__sprite.rect.topleft = self.__x, self.__y # type: ignore
        self.__sprite.dirty = 1

class Piece1Entity(Entity):
    def __init__(self, x, y):
        super().__init__()
        self.__x = x
        self.__y = y
        a = random.randint(32,64)
        p1ed = pygame.transform.scale(all_assets.p1ed_sprite, (a,a))
        self.__sprite = make_sprite(p1ed, (x, y))
        self.p1ed_rect = self.__sprite.rect

    def _spawned(self):
        self.show_sprite(self.__sprite)

    def _tick(self):
        self.__x += 200 * game.delta_time
        if self.__x > 1000:
            self.__x = 1000
        self.__sprite.rect.topleft = self.__x, self.__y # type: ignore
        self.__sprite.dirty = 1
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

    def compteur(self,temps):
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
        p10ed_number = random.randint(1,5)
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
        self.__x = x
        self.__y = y
        a = random.randint(32, 64)
        p10ed = pygame.transform.scale(all_assets.p10ed_sprite, (a,a))
        self.__sprite = make_sprite(p10ed, (x, y))
        self.p10ed_rect = self.__sprite.rect

    def _spawned(self):
        self.show_sprite(self.__sprite)

    def _tick(self):
        self.__x += 200 * game.delta_time
        if self.__x > game.viewport[0] - 700:
            self.__x = game.viewport[0] - 700
        self.__sprite.rect.topleft = self.__x, self.__y  # type: ignore
        self.__sprite.dirty = 1
        if self.p10ed_rect.colliderect(Rect(750, 0, 100, 700)):
            game.world.destroy_entity(self)

class ProjEntity(Entity):
    def __init__(self,x,y):
        super().__init__()
        self.__x = x
        self.__y = y


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