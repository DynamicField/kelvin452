import pygame.cursors
import pygame.transform

from kelvin452.engine import *
import random

from kelvin452.game.grounds import *
from kelvin452.game.score import *
from kelvin452.game.enemy import *
import kelvin452.game.life as life


class FireEntity(Entity, ReactsToCollisions):
    def __init__(self, x, y):
        super().__init__()
        self.position = Vector2(x, y)
        self.shoot_cooldown = 1
        self.timer = 0.1
        self.huge_fire_sprite = pygame.transform.scale(assets.sprite("fire.png"), (90, 90))
        self.__sprite = self.attach_component(make_sprite(self.huge_fire_sprite, (x, y)))
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
        if self.position.x < -100:
            game.world.destroy_entity(self)

    def _on_collide(self, other: Entity):
        if type(other) in CoinSpawner.get_coin_list():
            if hasattr(other, 'reward'):
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
        self.size = random.randint(32, 64)
        self.huge_coin_sprite = pygame.transform.scale(assets.sprite("classic_coin.png"), (self.size, self.size))
        self.__sprite = self.attach_component(make_sprite(self.huge_coin_sprite, (self.position.x, self.position.y)))
        self.__collision = self.attach_component(CollisionHitBox(follow_sprite_rect=True, draw_box=False))

    def _tick(self):
        self.position.x += 200 * game.delta_time
        if self.position.x > 1280:
            game.world.destroy_entity(self)
            life.modify_life(-1)


class WizardCoinEntity(Entity):
    def __init__(self, x, y):
        super().__init__()
        self.reward = 2
        self.position = Vector2(x, y)
        self.position_backup = self.position
        self.shoot_cooldown = random.randint(1, 2)
        self.timer = self.shoot_cooldown
        self.size = random.randint(32, 64)
        self.huge_coin_sprite = pygame.transform.scale(assets.sprite("wizard_coin.png"), (self.size, self.size))
        self.__sprite = self.attach_component(make_sprite(self.huge_coin_sprite, (self.position.x, self.position.y)))
        self.__collision = self.attach_component((CollisionHitBox(follow_sprite_rect=True, draw_box=False)))

    def _tick(self):
        if self.position.x >= 575:
            self.timer -= game.delta_time
            if self.timer <= 0:
                projectile_entity = WizardProjectileEntity(self.position.x, self.position.y - random.randint(-19, 19))
                game.world.spawn_entity(projectile_entity)
                self.timer = self.shoot_cooldown
                self.position = self.position_backup.copy()
        else:
            if self.position.x > 580:
                self.position.x = 580
            else:
                self.position.x += 200 * game.delta_time

        # milkshake moment !
        if self.timer < 0.5 and game.time_factor != 0:
            self.position.x = self.position_backup.x + random.randint(-4, 4)
            self.position.y = self.position_backup.y + random.randint(-4, 4)
        else:
            self.position_backup = self.position.copy()

    def set_cooldown(self, value):
        self.shoot_cooldown = value


class WizardProjectileEntity(Entity, ReactsToCollisions):
    def __init__(self, x, y):
        super().__init__()
        self.position = Vector2(x, y)
        self.__launched = False
        huge_projectile_sprite = pygame.transform.scale(assets.sprite("wizard_projectile.png"), (94, 38))
        self.__sprite = self.attach_component(make_sprite(huge_projectile_sprite, (self.position.x, self.position.y)))
        self.__collision = self.attach_component(CollisionHitBox(follow_sprite_rect=True, draw_box=False))

    def _tick(self):
        self.position.x += 600 * game.delta_time
        if self.position.x > 1200:
            game.world.destroy_entity(self)
            life.modify_life(-1)

    def _on_collide(self, other: Entity):
        if isinstance(other, FireEntity):
            game.world.destroy_entity(self)


class CoinSpawner(Entity):
    coins_list_setup = [(ClassicCoinEntity, 1, 100 / 100), (WizardCoinEntity, 2, 80 / 100)]

    @staticmethod
    def get_coin_list():
        coin_list = []
        for i in range(len(CoinSpawner.coins_list_setup)):
            coin_list.append(CoinSpawner.coins_list_setup[i][0])
        return coin_list

    def __init__(self):
        super().__init__()

        # self.coins_list : [(name, cost, probability / 100), (name, cost, probability / 100)]

        self.level = 1
        self.spawn_points = self.level ** 2  # the number of points the game will use by wave to spawn coins
        self.wave = True
        self.spawn_cooldown = 0.3
        self.spawn_timer = 0
        self.pre_wave_counter = False
        self.pre_wave_timer = 5

        self.spawn_list = []

    def spawn_listing(self):
        # time to choose the coins who will spawn
        print(f"spawnpoint : {self.spawn_points}")
        for i in range(-1, - 1 - len(self.coins_list_setup), -1):
            print(f"i : {i}")
            probability = self.coins_list_setup[i][2]
            cost = self.coins_list_setup[i][1]
            print(f"cost : {cost}")
            while (self.spawn_points >= cost) and (random.randint(1, 100) / 100 >= 1 - probability):
                self.spawn_points -= cost
                print(f"spawnpoint : {self.spawn_points}")
                self.spawn_list.append(self.coins_list_setup[i][0])

        # Now, randomizing for the spawning list
        random.shuffle(self.spawn_list)

    def no_coins(self):  # it will look if all coins are dead
        for i in self.get_coin_list():
            if len(game.world.get_entities(i)) != 0:
                return False
        return True

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
        if CoinSpawner.no_coins(self) and not self.pre_wave_counter:
            self.level += 1
            self.spawn_list = []
            self.spawn_points = self.level ** 2
            self.pre_wave_counter = True

        if self.pre_wave_counter:
            if self.pre_wave_timer > 0:
                self.pre_wave_timer -= game.delta_time
            else:
                self.wave = True


def start_menu():
    game.renderer.background = assets.grounds("menu_background.png")
    start_button = StartButtonEntity()
    game.world.spawn_entity(start_button)


class StartButtonEntity(Entity):
    def __init__(self, x=640, y=360):
        super().__init__()
        self.huge_x = 400
        self.huge_y = 120
        self.position = Vector2(x - self.huge_x / 2, y - self.huge_y / 2)
        self.huge_button_sprite = pygame.transform.scale(assets.sprite("start_game_button.png"),
                                                         (self.huge_x, self.huge_y))
        self.__sprite = self.attach_component(make_sprite(self.huge_button_sprite, self.position))
        # self.__collision = self.attach_component((CollisionHitBox(follow_sprite_rect=True, draw_box=True)))

    def _tick(self):
        if (self.position.x <= pygame.mouse.get_pos()[0] <= self.position.x + self.huge_x) and (
                self.position.y <= pygame.mouse.get_pos()[1] <= self.position.y + self.huge_y):
            if pygame.mouse.get_pressed()[0]:
                print("test")
                for entity in game.world.get_entities():
                    entity.destroy()
                game_start()


class RestartButtonEntity(Entity):
    def __init__(self, x=640, y=500):

        super().__init__()
        self.huge_x = 400
        self.huge_y = 120
        self.position = Vector2(x - self.huge_x / 2, y - self.huge_y / 2)
        self.huge_button_sprite = pygame.transform.scale(assets.sprite("restart_button.png"),
                                                         (self.huge_x, self.huge_y))
        self.__sprite = self.attach_component(make_sprite(self.huge_button_sprite, self.position))
        # self.__collision = self.attach_component((CollisionHitBox(follow_sprite_rect=True, draw_box=True)))

    def _tick(self):
        global game_over
        if (self.position.x <= pygame.mouse.get_pos()[0] <= self.position.x + self.huge_x) and (
                self.position.y <= pygame.mouse.get_pos()[1] <= self.position.y + self.huge_y):
            if pygame.mouse.get_pressed()[0]:
                for entity in game.world.get_entities():
                    entity.destroy()
                game_over = False
                game_start()


def game_start():
    game.renderer.background = assets.grounds("background.png")
    foreground = Foreground()
    game.world.spawn_entity(foreground)
    objects = Objects()
    game.world.spawn_entity(objects)
    fire_entity = FireEntity(1024, 315)
    game.world.spawn_entity(fire_entity)
    game.world.spawn_entity(CoinSpawner())
    basic_score(0)
    game.world.spawn_entity(ScoreText())
    basic_enemy(0)
    game.world.spawn_entity(EnemyText())
    life.life = 1
    game.world.spawn_entity(life.LifeText())


def launch_game():
    game.initialize_game()
    game.on_start(start_menu)
    game.log_fps = False
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
        restart_button = RestartButtonEntity()
        game.world.spawn_entity(restart_button)


if __name__ == "__main__":
    launch_game()
