import pygame.transform

from kelvin452.engine import *
import random


class FireEntity(Entity):
    def __init__(self, x, y):
        super().__init__()
        self.position = Vector2(x, y)
        self.shoot_cooldown = 1
        self.timer = 0
        huge_fire_sprite = pygame.transform.scale(assets.sprite("fire.png"), (90, 90))
        self.__sprite = self.attach_component(make_sprite(huge_fire_sprite, (x, y)))

    def add_y(self, add):  # add is the value we add in position y value, for example y == 10, add_y(10) put y at 20
        self.position.y += add

    def _tick(self):
        self.timer -= game.delta_time
        if pygame.mouse.get_pressed()[0] or game.input.is_key_down(pygame.K_SPACE):
            if self.timer <= 0:
                dragon_entity = DragonEntity(self.position.x, self.position.y + 30)
                game.world.spawn_entity(dragon_entity)
                self.timer = self.shoot_cooldown

        if game.input.is_key_down(pygame.K_DOWN):
            if self.position.y + 100 <= 720:
                self.add_y(10)
        if game.input.is_key_down(pygame.K_UP):
            if self.position.y - 10 >= 0:
                self.add_y(-10)


class DragonEntity(Entity):
    def __init__(self, x, y):
        super().__init__()
        self.position = Vector2(x, y)
        huge_dragon_sprite = pygame.transform.scale(assets.sprite("dragon.png"), (60, 43))
        self.__sprite = self.attach_component(make_sprite(huge_dragon_sprite, (x, y)))

    def _tick(self):
        self.position.x -= 10
        if self.position.x < 0:
            game.world.destroy_entity(self)


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
    game.log_fps = True
    game.renderer.background =
    fire_entity = FireEntity(1024, 315)
    game.world.spawn_entity(fire_entity)

    # partie d'alix en dessous
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
