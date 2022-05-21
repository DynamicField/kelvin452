import pygame.transform

from kelvin452.engine import *
import random


class FireEntity(Entity, ReactsToCollisions):
    def __init__(self, x, y):
        super().__init__()
        self.position = Vector2(x, y)
        self.shoot_cooldown = 1
        self.timer = 0
        huge_fire_sprite = pygame.transform.scale(assets.sprite("fire.png"), (90, 90))
        self.__sprite = self.attach_component(make_sprite(huge_fire_sprite, (x, y)))
        self.__collision = self.attach_component(CollisionHitBox(follow_sprite_rect=True, draw_box=False))

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
            if self.position.y + 100 <= 600:
                self.add_y(600*game.delta_time)
        if game.input.is_key_down(pygame.K_UP):
            if self.position.y - 10 >= 100:
                self.add_y(-600*game.delta_time)


class DragonEntity(Entity, ReactsToCollisions):
    def __init__(self, x, y):
        super().__init__()
        self.position = Vector2(x, y)
        huge_dragon_sprite = pygame.transform.scale(assets.sprite("dragon.png"), (60, 43))
        self.__sprite = self.attach_component(make_sprite(huge_dragon_sprite, (x, y)))
        self.__collision = self.attach_component(CollisionHitBox(follow_sprite_rect=True, draw_box=False))

    def _tick(self):
        self.position.x -= 600*game.delta_time
        if self.position.x < 0:
            game.world.destroy_entity(self)

    def _on_collide(self, other: Entity):
        if isinstance(other, Piece1Entity) or isinstance(other, Piece10Entity):
            game.world.destroy_entity(other)
            game.world.destroy_entity(self)


class Piece1Entity(Entity):
    def __init__(self, x, y):
        super().__init__()
        self.position = Vector2(x, y)
        a = random.randint(32, 64)
        p1ed = pygame.transform.scale(assets.sprite("p1ed.png"), (a, a))
        self.__sprite = self.attach_component(make_sprite(p1ed, (x, y)))
        self.__collision = self.attach_component(CollisionHitBox(follow_sprite_rect=True, draw_box=False))

    def _tick(self):
        self.position.x += 200 * game.delta_time
        if self.position.x > 900:
            self.position.x = 900


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
        b = [250, 340, 430]
        self.compteurino -= game.delta_time
        if self.compteurino <= 0:
            self.compte2 = True
            for i in range(3):
                if z >= 5:
                    z = 0
                p1ed_entity = Piece1Entity(0, b[z])
                game.world.spawn_entity(p1ed_entity)
                z += 1
            self.compteurino = temps

    def compteur2(self, temps):
        z = 0
        b = [250, 340, 430]
        p10ed_number = random.randint(1, 3)
        self.compteuridos -= game.delta_time
        if self.compteuridos <= 0:
            for i in range(p10ed_number):
                if z >= 3:
                    z = 0
                p10ed_entity = Piece10Entity(0, b[z])
                game.world.spawn_entity(p10ed_entity)
                z += 1
            self.compteuridos = temps
            self.compte2 = False


class Piece10Entity(Entity):
    def __init__(self, x, y):
        super().__init__()
        self.position = Vector2(x, y)
        self.compteurProj = random.uniform(4, 6)
        self.compteurProjRes = self.compteurProj
        a = random.randint(32, 64)
        p10ed = pygame.transform.scale(assets.sprite("p10ed.png"), (a, a))
        self.__sprite = self.attach_component(make_sprite(p10ed, (x, y)))
        self.__collision = self.attach_component(CollisionHitBox(follow_sprite_rect=True, draw_box=False))

    def _tick(self):
        if self.position.x >= 575:
            self.compteurProj -= game.delta_time
            if self.compteurProj <= 0:
                proj_entity = ProjEntity(self.position.x, self.position.y - random.randint(0, 50))
                game.world.spawn_entity(proj_entity)
                self.compteurProj = 1
        self.position.x += 200 * game.delta_time
        if self.position.x > 580:
            self.position.x = 580


class ProjEntity(Entity, ReactsToCollisions):
    def __init__(self, x, y):
        super().__init__()
        self.position = Vector2(x, y)
        self.__launched = False
        proj = pygame.transform.scale(assets.sprite("projectile.png"), (100, 100))
        self.__sprite = self.attach_component(make_sprite(proj, (x, y)))
        self.__collision = self.attach_component(CollisionHitBox(follow_sprite_rect=True, draw_box=False))

    def _tick(self):
        self.position.x += 10
        if self.position.x > 1200:
            game.world.destroy_entity(self)

    def _on_collide(self, other: Entity):
        if isinstance(other, FireEntity):
            game.world.destroy_entity(self)


def game_start():
    game.log_fps = True
    game.renderer.background = assets.background("background.png")
    fire_entity = FireEntity(1024, 315)
    game.world.spawn_entity(fire_entity)

    # partie d'alix en dessous
    z = 0
    b = [250, 340, 430]
    spawner = Entity_spawn()
    game.world.spawn_entity(spawner)
    for i in range(3):
        if z >= 3:
            z = 0
        p1ed_entity = Piece1Entity(0, b[z])
        game.world.spawn_entity(p1ed_entity)
        z += 1


def launch_game():
    game.initialize_game()
    game.on_start(game_start)
    game.start()


def end_game():
    game.renderer.background = assets.background("game_over.png")


if __name__ == "__main__":
    launch_game()
