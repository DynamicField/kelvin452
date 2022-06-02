import pygame.cursors
import pygame.transform

from kelvin452.engine import *
import random

from kelvin452.game.grounds import *
from kelvin452.game.score import *
from kelvin452.game.enemy import *
from kelvin452.game.life import *


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
            if self.timer <= 0 and game.time_factor != 0:
                dragon_entity = DragonEntity(self.position.x, self.position.y + 30)
                game.world.spawn_entity(dragon_entity)
                self.timer = self.shoot_cooldown

        if game.input.is_key_down(pygame.K_DOWN):
            if self.position.y + 100 <= 600:
                self.add_y(600 * game.delta_time)
        if game.input.is_key_down(pygame.K_UP):
            if self.position.y - 10 >= 100:
                self.add_y(-600 * game.delta_time)


class DragonEntity(Entity, ReactsToCollisions):
    def __init__(self, x, y):
        super().__init__()
        self.position = Vector2(x, y)
        huge_dragon_sprite = pygame.transform.scale(assets.sprite("dragon.png"), (60, 43))
        self.__sprite = self.attach_component(make_sprite(huge_dragon_sprite, (x, y)))
        self.__collision = self.attach_component(CollisionHitBox(follow_sprite_rect=True, draw_box=False))

    def _tick(self):
        self.position.x -= 600 * game.delta_time
        if self.position.x < 0:
            game.world.destroy_entity(self)

    def _on_collide(self, other: Entity):
        if isinstance(other, ClassicCoinEntity):  # or isinstance(other, Piece10Entity):
            add_score(other.reward)
            modify_enemy(other.reward)
            for _ in range(other.reward):
                enemy_entity = EnemyEntity()
                game.world.spawn_entity(enemy_entity)
            game.world.destroy_entity(other)
            game.world.destroy_entity(self)


class EnemyEntity(Entity):
    def __init__(self):
        super().__init__()
        self.huge_x = 34  # largeur x du sprite
        self.huge_y = 54  # hauteur y du sprite
        self.position = Vector2(random.randint(1144, 1253 - self.huge_x), random.randint(400, 533))
        huge_enemy_sprite = pygame.transform.scale(assets.sprite("enemy1.png"), (self.huge_x, self.huge_y))
        self.__sprite = self.attach_component(make_sprite(huge_enemy_sprite, self.position))

    def _tick(self):
        if self.position.y < 602 - self.huge_y:
            if self.position.y + 10 >= 602 - self.huge_y:
                self.position.y += (602 - self.huge_y - self.position.y)
            else:
                self.position.y += 300 * game.delta_time


class ClassicCoinEntity(Entity):
    def __init__(self, x, y):
        super().__init__()
        self.reward = 1
        self.position = Vector2(x, y)
        size = random.randint(32, 64)
        coin = pygame.transform.scale(assets.sprite("classic_coin.png"), (size, size))
        self.__sprite = self.attach_component(make_sprite(coin, (self.position.x, self.position.y)))
        self.__collision = self.attach_component(CollisionHitBox(follow_sprite_rect=True, draw_box=False))

    def _tick(self):
        self.position.x += 200 * game.delta_time
        if self.position.x > 1280:
            game.world.destroy_entity(self)
            modify_life(-1)


class CoinSpawner(Entity):
    def __init__(self):
        super().__init__()

        # self.coins_list : [(name, cost, probability / 100), (name, cost, probability / 100)]
        self.coins_list = [(ClassicCoinEntity, 1, 100 / 100)]  # , (MageCoinEntity, 2, 50 / 100)]
        self.level = 1
        self.spawn_points = self.level ** 2  # the number of points the game will use by wave to spawn coins
        self.wave = True
        self.spawn_cooldown = 0.2
        self.spawn_timer = 0
        self.pre_wave_counter = False
        self.pre_wave_timer = 5

        self.spawn_list = []

    def spawn_listing(self):
        # time to choose the coins who will spawn
        index = -1  # the index for the coin_list
        while self.spawn_points > 0:
            if self.coins_list[index][1] <= self.spawn_points:
                if (random.randint(1, 100) / 100) <= self.coins_list[index][2]:
                    self.spawn_points -= self.coins_list[index][1]
                    self.spawn_list.append(self.coins_list[index][0])
                else:
                    if -index == len(self.coins_list):
                        index = -1
                    else:
                        index -= 1

        # Now, randomizing for the spawning list
        random.shuffle(self.spawn_list)

    def _tick(self):
        if self.wave:
            self.spawn_listing()
            self.wave = False

        # spawning part
        if self.spawn_timer <= 0 and self.spawn_list != []:
            game.world.spawn_entity((self.spawn_list.pop())(0, random.randint(258, 503)))
            self.spawn_timer = self.spawn_cooldown
            self.pre_wave_timer = 5
            self.pre_wave_counter = False

        self.spawn_timer -= game.delta_time

        # wave ending
        if len(game.world.get_entities(ClassicCoinEntity)) == 0 and not self.pre_wave_counter:
            self.level += 1
            self.spawn_list = []
            self.spawn_points = self.level ** 2
            self.pre_wave_counter = True

        if self.pre_wave_counter:
            if self.pre_wave_timer > 0:
                self.pre_wave_timer -= game.delta_time
            else:
                self.wave = True


def game_start():
    game.log_fps = False
    game.renderer.background = assets.grounds("background.png")
    foreground = Foreground()
    game.world.spawn_entity(foreground)
    objects = Objects()
    game.world.spawn_entity(objects)
    fire_entity = FireEntity(1024, 315)
    game.world.spawn_entity(fire_entity)
    game.world.spawn_entity(CoinSpawner())
    game.world.spawn_entity(ScoreText())
    game.world.spawn_entity(EnemyText())
    game.world.spawn_entity(LifeText())


def launch_game():
    game.initialize_game()
    game.on_start(game_start)
    game.start()


game_over = False


def end_game():
    global game_over
    if not game_over:
        game_over = True
        game.renderer.background = assets.grounds("game_over.png")
        for entity in game.world.get_entities():
            # Pas toutes les entités ont l'attribut survive_game_over
            # alors on utilise getattr pour avoir une valeur par défaut de False
            if not getattr(entity, "survive_game_over", False):
                entity.destroy()


if __name__ == "__main__":
    launch_game()
