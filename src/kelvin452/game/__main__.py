import pygame.cursors
import pygame.transform

from kelvin452.engine import *
import random
import math
import csv

from kelvin452.game.grounds import *
from kelvin452.game.score import *
import kelvin452.game.level as level
import kelvin452.game.enemy as enemy_module
import kelvin452.game.powers as powers
import kelvin452.game.life as life
from collections import namedtuple


def ultimate_random_total(min, max):
    return random.randint(min, max)


class FireEntity(Entity, EventConsumer):
    def __init__(self, x, y):
        super().__init__()
        self.position = Vector2(x, y)
        self.powers = powers.Powers()
        self.timer = 0.1
        self.huge_fire_sprite = pygame.transform.scale(assets.sprite("fire.png"), (90, 90))
        self.__sprite = self.attach_component(make_sprite(self.huge_fire_sprite, (x, y)))
        self.__collision = self.attach_component(CollisionHitBox(follow_sprite_rect=True, draw_box=False))
        self.click_allowed = False

    def add_y(self, add):  # add is the value we add in position y value, for example y == 10, add_y(10) put y at 20
        self.position.y += add

    def consume_event(self, new_event: pygame.event.Event) -> bool:
        if new_event.type == pygame.MOUSEBUTTONDOWN:
            self.click_allowed = True
            return True
        return False

    def get_priority(self):
        return -1

    def _tick(self):
        self.timer -= game.delta_time

        if game.world.get_single_entity(powers.PowerupMenu) is not None:
            return

        if (self.click_allowed and pygame.mouse.get_pressed()[0]) or game.input.is_key_down(pygame.K_SPACE):
            self.spawn_dragon()
        else:
            self.click_allowed = False

        if game.input.is_key_down(pygame.K_DOWN) or game.input.is_key_down(pygame.K_s):
            if self.position.y + 100 <= 600:
                self.add_y(600 * game.delta_time)
        if game.input.is_key_down(pygame.K_UP) or game.input.is_key_down(pygame.K_z):
            if self.position.y - 10 >= 100:
                self.add_y(-600 * game.delta_time)

    def spawn_dragon(self):
        if self.timer <= 0 and game.time_factor != 0:
            dragon_entity = DragonEntity(self.powers.coins_pierced, self.powers.damage, self.position.x,
                                         self.position.y + 30)
            game.world.spawn_entity(dragon_entity)
            self.timer = self.powers.fire_rate


class DragonEntity(Entity, ReactsToCollisions):
    def __init__(self, durability, damage, x, y):
        super().__init__()
        self.durability = durability
        self.damage = damage
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
                other.dragon_touch(self.damage)
                if self.durability == 1:
                    game.world.destroy_entity(self)
                else:
                    self.durability -= 1
        elif type(other) == EldenWizardEntity:
            other.dragon_touch(self.damage)
            if self.durability == 1:
                game.world.destroy_entity(self)
            else:
                self.durability -= 1


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
        self.pv = CoinSpawner.get_coin_pv(ClassicCoinEntity)
        self.reward = 1
        self.position = Vector2(x, y)
        self.size = random.randint(32, 64)
        self.huge_coin_sprite = pygame.transform.scale(assets.sprite("classic_coin.png"), (self.size, self.size))
        self.__sprite = self.attach_component(make_sprite(self.huge_coin_sprite, (self.position.x, self.position.y)))
        self.__collision = self.attach_component(CollisionHitBox(follow_sprite_rect=True, draw_box=False))

    def dragon_touch(self, damage):
        self.pv -= damage

    def _tick(self):
        if self.pv <= 0:
            add_score(self.reward)
            enemy_module.modify_enemy(self.reward)
            self.destroy()

        self.position.x += 200 * game.delta_time
        if self.position.x > 1280:
            game.world.destroy_entity(self)
            life.modify_life(-1)


class WizardCoinEntity(Entity):
    def __init__(self, x, y):
        super().__init__()
        self.pv = CoinSpawner.get_coin_pv(WizardCoinEntity)
        self.reward = 2
        self.position = Vector2(x, y)
        self.position_backup = self.position
        self.shoot_cooldown = random.randint(1, 2)
        self.timer = self.shoot_cooldown
        self.height = random.randint(32, 64)
        self.length = (29 * self.height) // 30
        self.huge_coin_sprite = pygame.transform.scale(assets.sprite("wizard_coin.png"), (self.length, self.height))
        self.__sprite = self.attach_component(make_sprite(self.huge_coin_sprite, (self.position.x, self.position.y)))
        self.__collision = self.attach_component((CollisionHitBox(follow_sprite_rect=True, draw_box=False)))

    def dragon_touch(self, damage):
        self.pv -= damage

    def _tick(self):
        if self.pv <= 0:
            add_score(self.reward)
            enemy_module.modify_enemy(self.reward)
            self.destroy()
        if self.position.x >= 575:
            self.timer -= game.delta_time
            if self.timer <= 0:
                projectile_entity = WizardProjectileEntity(self.position.x, self.position.y,
                                                           self)
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
    def __init__(self, x, y, wizard):
        super().__init__()
        self.height = wizard.height / 2
        self.length = (13 * self.height) / 10
        self.position = Vector2(x + (26 * wizard.length) / 29, y + (12.5 * wizard.height) / 30 - self.height / 2)
        huge_projectile_sprite = pygame.transform.scale(assets.sprite("wizard_projectile.png"),
                                                        (self.length, self.height))
        self.__sprite = self.attach_component(make_sprite(huge_projectile_sprite, (self.position.x, self.position.y)))
        self.__collision = self.attach_component(CollisionHitBox(follow_sprite_rect=True, draw_box=False))
        self.trail = WizardProjectileTrailEntity(self.position.x, self.position.y, self)
        self.trail.projectile = self
        game.world.spawn_entity(self.trail)

    def _tick(self):
        self.position.x += 600 * game.delta_time
        if self.position.x > 1200:
            game.world.destroy_entity(self)
            life.modify_life(-1)

    def _on_collide(self, other: Entity):
        if isinstance(other, FireEntity):
            game.world.destroy_entity(self)


class WizardProjectileTrailEntity(Entity):
    def __init__(self, x, y, projectile):
        super().__init__()
        self.projectile = projectile
        self.height = (12 * projectile.height) / 10
        self.length = (30 * projectile.length) / 13
        self.position = Vector2(x - (16 * self.length) // 30, y - self.height // 12)
        huge_projectile_trail_sprite = pygame.transform.scale(assets.sprite("wizard_projectile_trail.png"),
                                                              (self.length,
                                                               self.height))
        self.__sprite = self.attach_component(
            make_sprite(huge_projectile_trail_sprite, (self.position.x, self.position.y)))

    def _tick(self):
        if self.projectile.is_alive:
            if self.position.x != self.projectile.position.x:
                self.position.x = self.projectile.position.x - (16 * self.length) / 30
        else:
            game.world.destroy_entity(self)


class KnightCoinEntity(Entity):
    def __init__(self, x, y):
        super().__init__()
        self.pv = CoinSpawner.get_coin_pv(KnightCoinEntity)
        self.armored = True
        self.reward = 3
        self.position = Vector2(x, y)
        self.size = random.randint(32, 64)
        self.huge_coin_sprite = pygame.transform.scale(assets.sprite("armored_knight_coin.png"), (self.size, self.size))
        self.__sprite = self.attach_component(make_sprite(self.huge_coin_sprite, (self.position.x, self.position.y)))
        self.__collision = self.attach_component((CollisionHitBox(follow_sprite_rect=True, draw_box=False)))

    def dragon_touch(self, damage):
        self.pv -= damage

    def _tick(self):
        if self.pv <= 0:
            add_score(self.reward)
            enemy_module.modify_enemy(self.reward)
            self.destroy()

        if 0 < self.pv <= CoinSpawner.get_coin_pv(KnightCoinEntity) // 2 and self.armored:
            self.huge_coin_sprite = pygame.transform.scale(assets.sprite("naked_knight_coin.png"),
                                                           (self.size, self.size))
            self.__sprite = self.attach_component(
                make_sprite(self.huge_coin_sprite, (self.position.x, self.position.y)))
            self.armored = False

        self.position.x += 150 * game.delta_time
        if self.position.x > 1280:
            game.world.destroy_entity(self)
            life.modify_life(-1)


class EldenWizardEntity(Entity):
    def __init__(self, x, y):
        super().__init__()
        self.shoot_cooldown = 2
        self.shield_cooldown = 0
        self.timer = self.shoot_cooldown
        self.phase = 1
        self.pv = 4
        self.pv_max = self.pv
        self.position = Vector2(x, y)
        self.move_goal = self.position
        self.moving_direction = None  # if the Coin move in the x or y axe
        self.moving_speed = 1
        self.height = 149
        self.length = 79
        self.huge_coin_sprite = pygame.transform.scale(assets.sprite("elden_wizard.png"), (self.length, self.height))
        self.__sprite = self.attach_component(make_sprite(self.huge_coin_sprite, (self.position.x, self.position.y)))
        self.__collision = self.attach_component(CollisionHitBox(follow_sprite_rect=True, draw_box=False))

        # spawning health bar
        self.health_bar = EldenWizardHealthBar(self)
        game.world.spawn_entity(self.health_bar)

    def dragon_touch(self, damage):
        self.pv -= damage

        if self.pv / self.pv_max > 0.75 and self.phase != 1:
            self.phase_one()

        elif 0.5 < self.pv / self.pv_max <= 0.75 and self.phase != 2:
            self.phase_two()

        elif 0.25 < self.pv / self.pv_max <= 0.5 and self.phase != 3:
            self.phase_three()

        elif self.pv / self.pv_max < 0.25:
            self.phase_four()

    def moving_goal(self):
        self.move_goal, self.moving_direction = (random.randint(0, 575), random.randint(100, 500)), random.randint(1, 2)

    def phase_one(self):
        # start the phase one
        if self.phase != 1:
            self.phase = 1
            self.set_cooldown(2)
            self.move_goal, self.moving_direction = self.moving_goal()[0]

        # this one is for utilities in the phase (x or y and move goal currently)

    def phase_two(self):
        # start the phase two
        if self.phase != 2:
            self.phase = 2
            self.set_cooldown(2)

    def phase_three(self):
        self.phase = 3

    def phase_four(self):
        self.phase = 4

    def _tick(self):
        if self.pv <= 0:
            add_score(100)
            self.destroy()

        if self.phase == 1:
            self.timer -= game.delta_time
            if self.timer <= 0:
                projectile_entity = EldenWizardProjectileEntity(self.position.x + 49, self.position.y + 39,
                                                                self, (24, 60))
                game.world.spawn_entity(projectile_entity)
                self.timer = self.shoot_cooldown
            if self.position == self.move_goal:
                self.moving_goal()
            elif self.moving_direction == 1 and self.move_goal[0] - 10 <= self.position.x <= self.move_goal[0] + 10:
                self.position.x = self.move_goal[0]
                self.moving_direction = 2
            elif self.moving_direction == 2 and self.move_goal[1] - 10 <= self.position.y <= self.move_goal[1] + 10:
                self.position.y = self.move_goal[1]
                self.moving_direction = 1

            elif self.moving_direction == 1:
                if self.move_goal[0] - self.position.x < 0:
                    self.position.x -= 200 * game.delta_time * self.moving_speed
                else:
                    self.position.x += 200 * game.delta_time * self.moving_speed
                # don't leave the screen!
                if self.position.x > 575:
                    self.position.x = 575
                elif self.position.x < 0:
                    self.position.x = 0

            elif self.moving_direction == 2:
                if self.move_goal[1] - self.position.y < 0:
                    self.position.y -= 200 * game.delta_time * self.moving_speed
                else:
                    self.position.y += 200 * game.delta_time * self.moving_speed
                if self.position.y > 600:
                    self.position.x = 600
                elif self.position.x < 100:
                    self.position.x = 100
            self.moving_speed += self.moving_speed / 100 * game.delta_time
            self.shoot_cooldown += self.shoot_cooldown / 100 * game.delta_time

        elif self.phase == 2:
            self.timer -= game.delta_time
            if self.timer <= 0:
                projectile_entity = EldenWizardProjectileEntity(self.position.x + 49, self.position.y + 39,
                                                                self, (24, 60))
                game.world.spawn_entity(projectile_entity)
                self.timer = self.shoot_cooldown
            if self.position == self.move_goal:
                self.moving_goal()
            elif self.moving_direction == 1 and self.move_goal[0] - 10 <= self.position.x <= self.move_goal[0] + 10:
                self.position.x = self.move_goal[0]
                self.moving_direction = 2
            elif self.moving_direction == 2 and self.move_goal[1] - 10 <= self.position.y <= self.move_goal[1] + 10:
                self.position.y = self.move_goal[1]
                self.moving_direction = 1

            elif self.moving_direction == 1:
                if self.move_goal[0] - self.position.x < 0:
                    self.position.x -= 200 * game.delta_time * self.moving_speed
                else:
                    self.position.x += 200 * game.delta_time * self.moving_speed
                # don't leave the screen!
                if self.position.x > 575:
                    self.position.x = 575
                elif self.position.x < 0:
                    self.position.x = 0

            elif self.moving_direction == 2:
                if self.move_goal[1] - self.position.y < 0:
                    self.position.y -= 200 * game.delta_time * self.moving_speed
                else:
                    self.position.y += 200 * game.delta_time * self.moving_speed
                if self.position.y > 600:
                    self.position.x = 600
                elif self.position.x < 100:
                    self.position.x = 100
            self.moving_speed += self.moving_speed / 2 / 100 * game.delta_time

            if self.shield_cooldown <= 0:
                game.world.spawn_entity(EldenWizardCrystalShieldEntity(self.position.x, self.position.y, self))
                # self.shield_cooldown = 5

    def set_cooldown(self, value):
        self.shoot_cooldown = value


class EldenWizardProjectileEntity(Entity, ReactsToCollisions):
    def __init__(self, x, y, wizard, size: tuple = (12, 30), mode=1):
        super().__init__()
        self.type = mode
        self.height, self.length = size
        self.position = Vector2(x, y)

        huge_projectile_sprite = None
        if self.type == 1:
            huge_projectile_sprite = pygame.transform.scale(assets.sprite("elden_wizard_safe_projectile.png"),
                                                            (self.length, self.height))
        elif self.type == 2:
            huge_projectile_sprite = pygame.transform.scale(assets.sprite("elden_wizard_lethal_projectile.png"),
                                                            (self.length, self.height))
        self.__sprite = self.attach_component(make_sprite(huge_projectile_sprite, (self.position.x, self.position.y)))
        self.__collision = self.attach_component(CollisionHitBox(follow_sprite_rect=True, draw_box=False))

    def _tick(self):
        self.position.x += 600 * game.delta_time
        if self.position.x > 1200:
            if self.type == 1:
                life.modify_life(-1)
            game.world.destroy_entity(self)

    def _on_collide(self, other: Entity):
        if isinstance(other, FireEntity):
            if self.type == 2:
                life.modify_life(-1)
            game.world.destroy_entity(self)


class EldenWizardCrystalShieldEntity(Entity):
    def __init__(self, x, y, elden_wizard):
        super().__init__()
        self.elden_wizard = elden_wizard
        self.radiant = math.pi
        self.position = Vector2(x, y)
        # self.original_position = self.position
        self.height = 20
        self.length = 21
        self.huge_coin_sprite = pygame.transform.scale(assets.sprite("elden_wizard_crystal_shield.png"),
                                                       (self.height, self.length))
        self.__sprite = self.attach_component(make_sprite(self.huge_coin_sprite, (self.position.x, self.position.y)))
        self.__collision = self.attach_component(CollisionHitBox(follow_sprite_rect=True, draw_box=False))

    def _tick(self):
        self.radiant -= 2 * game.delta_time
        self.position = self.elden_wizard.position.x + math.cos(
            self.radiant) * 120 + 33 - self.length // 2, self.elden_wizard.position.y + math.sin(
            self.radiant) * 120 + 79 - self.height // 2


class EldenWizardHealthBar(Entity):
    def __init__(self, elden_wizard, x=289, y=24):
        super().__init__()
        self.elden_wizard = elden_wizard
        self.position = Vector2(x, y)
        self.height = 21
        self.length = 700
        self.length_max = self.length  # for the proportion
        self.huge_bar_sprite = pygame.transform.scale(assets.sprite("barre_pv_boss(temporaire).png"), (self.length,
                                                                                                       self.height))
        self.__sprite = self.attach_component(
            KelvinSprite(self.huge_bar_sprite, (self.position.x, self.position.y), layer=300))

    def _tick(self):
        if (self.elden_wizard.pv / self.elden_wizard.pv_max) != (self.length / self.length_max):
            self.length = (self.elden_wizard.pv * self.length_max) / self.elden_wizard.pv_max

            # reload the sprite
            self.__sprite.image = pygame.transform.scale(assets.sprite("barre_pv_boss(temporaire).png"), (self.length,
                                                                                                          self.height))
            self.__sprite.dirty = 1


class CoinSpawner(Entity):
    # [(name, cost, probability / 100), pv]
    coins_list_setup = [(ClassicCoinEntity, 1, 100 / 100, 1), (WizardCoinEntity, 2, 80 / 100, 1),
                        (KnightCoinEntity, 5, 75 / 100, 2)]

    @staticmethod
    def get_coin_list():
        coin_list = []
        for i in range(len(CoinSpawner.coins_list_setup)):
            coin_list.append(CoinSpawner.coins_list_setup[i][0])
        return coin_list

    @staticmethod
    def get_coin_pv(name):
        for i in range(len(CoinSpawner.coins_list_setup)):
            if CoinSpawner.coins_list_setup[i][0] == name:
                return CoinSpawner.coins_list_setup[i][3]

    def __init__(self):
        super().__init__()

        # self.coins_list : [(name, cost, probability / 100), pv , (name, pv, cost, probability / 100), pv]

        # the number of points the game will use by wave to spawn coins
        self.spawn_points = 0
        self.wave = True
        self.spawn_cooldown = 0.3
        self.spawn_timer = 0
        self.pre_wave_counter = False
        self.pre_wave_timer = 5
        self.paused = False
        self.powerup_time = False

        self.spawn_list = []
        self.random_y = 300
        self.previous_y = 300

        # for the csv file
        self.csv_equation = "(1 / math.sqrt(5)) * ((phi ** x) - (-1 / phi) ** x)"
        self.csv_spawnpoint = 0
        self.csv_nbr_coin = 0
        self.csv_nbr_wizard = 0
        self.csv_nbr_knight = 0

    def compute_spawn_point(self):
        print(f"the fucking level is {level.level}")
        x = level.level
        # it calculates the numbers of points who will use by wave to spawn coins
        phi = (1 + math.sqrt(5)) / 2
        equation = (1 / math.sqrt(5)) * ((phi ** x) - (-1 / phi) ** x)
        return x ** 2  # equation

    def spawn_listing(self):
        # time to choose the coins who will spawn
        self.spawn_points = self.compute_spawn_point()
        self.csv_spawnpoint = self.spawn_points
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

        # we take the number of coins for each type:
        self.nbr_types_coins_csv_log()

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

        if not self.paused:
            # spawning part
            if self.spawn_timer <= 0 and self.spawn_list != []:
                # to make a real random spawn for y
                self.random_y = ultimate_random_total(200, 515)
                while self.previous_y - 50 <= self.random_y <= self.previous_y + 50:
                    self.random_y = ultimate_random_total(258, 503)
                game.world.spawn_entity(
                    (self.spawn_list.pop())(0, self.random_y))
                self.previous_y = self.random_y

                self.spawn_timer = self.spawn_cooldown
                self.pre_wave_timer = 4
                self.pre_wave_counter = False

            self.spawn_timer -= game.delta_time

            # wave ending
            if CoinSpawner.no_coins(self) and not self.pre_wave_counter:
                if level.level % 3 == 0:
                    self.powerup_time = True

                print(f"level = {level.level}")

                # time to write all in the log file
                with open('log_coin_spawner.csv', 'a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(
                        [self.csv_equation, level.level, self.csv_spawnpoint, self.csv_nbr_coin, self.csv_nbr_wizard,
                         self.csv_nbr_knight])
                    self.csv_nbr_coin, self.csv_nbr_wizard, self.csv_nbr_knight = 0, 0, 0

                self.pre_wave_counter = True

            if self.pre_wave_counter:
                if self.powerup_time and self.pre_wave_timer < 3:
                    self.show_powerup_menu()
                elif self.pre_wave_timer > 0:
                    self.pre_wave_timer -= game.delta_time
                else:
                    level.add_level()
                    self.spawn_list = []
                    self.wave = True

    def show_powerup_menu(self):
        def unpause():
            self.paused = False

        self.paused = True
        jean = JeanBoss()
        jean.destroyed_notifiers.append(unpause)
        game.world.spawn_entity(jean)
        self.powerup_time = False

    def nbr_types_coins_csv_log(self):  # it'll use self.spawn_list to find how many coin in each type
        for i in self.spawn_list:
            if i == ClassicCoinEntity:
                self.csv_nbr_coin += 1
            elif i == WizardCoinEntity:
                self.csv_nbr_wizard += 1
            elif i == KnightCoinEntity:
                self.csv_nbr_knight += 1


class JeanBoss(Entity, EventConsumer):
    Keyframe = namedtuple('Phase', ['start', 'duration', 'end'])

    def __init__(self):
        super().__init__()
        self.position = Vector2(-128, (game.viewport.y - 128) / 2)
        resized_image = pygame.transform.scale(assets.sprite("boss.png"), (128, 128))
        self.sprite = self.attach_component(KelvinSprite(resized_image))
        self.phase = 1
        self.anim1_time = 0.04
        self.animation_speed_multiplier = 1  # à changer si l'animation est trop lente
        self.flip_next_frame = False
        self.click_timer = None

    def consume_event(self, new_event: pygame.event.Event) -> bool:
        if self.click_timer is not None \
                and self.phase == 1 \
                and new_event.type == pygame.MOUSEBUTTONDOWN \
                and self.sprite.rect.collidepoint(game.input.get_mouse_position()):
            self.open_menu()
            return True
        return False

    def _tick(self):
        if self.flip_next_frame:
            self.flip()
            self.flip_next_frame = False

        if self.phase == 1:
            self.anim1_time += game.delta_time * self.animation_speed_multiplier
            k1 = self.keyframe(None, 0.5)  # Pause du début
            k2 = self.keyframe(k1, 0.8)  # Avancée et reculée
            k3 = self.keyframe(k2, 0.4)  # Pause avant de revenir pour de vrai
            if self.anim1_time < k1.end:
                pass  # Rien
            elif self.anim1_time < k2.end:
                # https://www.desmos.com/calculator/5v6nfruhwh
                time_from_start = (self.anim1_time - k2.start)
                self.position.x \
                    = -128 + 100 * min(-((2.2 * (time_from_start * (1 / k2.duration)) - 1.095) ** 2) + 1.20, 1)
            elif self.anim1_time < k3.end:
                pass  # Rien
            else:
                if self.position.x < 500:
                    self.position.x = min(self.position.x + 600 * game.delta_time, 500)
                elif self.click_timer is None:
                    self.click_timer = 3

                if self.click_timer is not None:
                    self.click_timer -= game.delta_time
                    if self.click_timer < 0:
                        self.phase = 3
                        self.flip_next_frame = True

        elif self.phase == 2:
            # Utiliser des keyframe à la place ?
            if self.position.x > 40:
                self.position.x = max(self.position.x - 400 * game.delta_time, 40)
                if self.position.x <= 40:
                    self.flip()
        elif self.phase == 3:
            if self.position.x > -200:
                self.position.x = max(self.position.x - 400 * game.delta_time, -200)
            else:
                self.destroy()  # bye !

    # Clé d'animation
    def keyframe(self, prev, duration) -> Keyframe:
        if prev is None:
            return JeanBoss.Keyframe(0, duration, duration)
        else:
            return JeanBoss.Keyframe(prev[2], duration, prev[2] + duration)

    def flip(self):
        self.sprite.image = pygame.transform.flip(self.sprite.image, flip_x=True, flip_y=False)
        self.sprite.dirty = 1

    def open_menu(self):
        menu = powers.PowerupMenu(game.world.get_single_entity(FireEntity).powers)
        menu.destroyed_notifiers.append(lambda: self.menu_destroyed())
        game.world.spawn_entity(menu)
        self.phase = 2
        self.flip_next_frame = True

    def menu_destroyed(self):
        self.phase = 3
        self.flip_next_frame = True


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
    game.world.spawn_entity(ScoreText())
    game.world.spawn_entity(level.LevelText())
    game.world.spawn_entity(enemy_module.EnemyText())
    game.world.spawn_entity(life.LifeText())
    elden_wizard = EldenWizardEntity(600, 315)
    game.world.spawn_entity(elden_wizard)

    fire_entity = FireEntity(1024, 315)
    game.world.spawn_entity(fire_entity)


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
