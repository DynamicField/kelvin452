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
        self.__collision = self.attach_component(CollisionHitBox(follow_sprite_rect=True, draw_box=True))

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
            if self.position.y + 100 <= 602:
                self.add_y(10)
        if game.input.is_key_down(pygame.K_UP):
            if self.position.y - 10 >= 100:
                self.add_y(-10)


class DragonEntity(Entity):
    def __init__(self, x, y):
        super().__init__()
        self.position = Vector2(x, y)
        huge_dragon_sprite = pygame.transform.scale(assets.sprite("dragon.png"), (60, 43))
        self.__sprite = self.attach_component(make_sprite(huge_dragon_sprite, (x, y)))
        self.__collision = self.attach_component(CollisionHitBox(follow_sprite_rect=True, draw_box=True))

    def _on_collide(self, other: Entity):
        print("oskour la collision vers " + str(other))

    def _tick(self):
        self.position.x -= 10
        if self.position.x < 0:
            game.world.destroy_entity(self)




def game_start():
    game.log_fps = True
    game.renderer.background = assets.background("background.png")
    fire_entity = FireEntity(1024, 315)
    game.world.spawn_entity(fire_entity)



def launch_game():
    game.initialize_game()
    game.on_start(game_start)
    game.start()


if __name__ == "__main__":
    launch_game()
