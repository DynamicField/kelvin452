import pygame

from kelvin452.engine import *
import kelvin452.game.__main__ as main
import kelvin452.game.level as level
import kelvin452.game.inventory as inventory


class EndDemo(Entity):
    def __init__(self):
        super().__init__()
        self.i = 2
        self.crystal_timer = 1
        self.ending = False
        self.click_allowed = 0.1

    def _tick(self):

        if self.crystal_timer <= 0 and not self.ending:
            game.time_factor = 0
            game.world.destroy_entity(game.world.get_single_entity(inventory.PiercingCrystalEntity))
            self.height = 428
            self.width = 700
            self.position = Vector2(1280 // 2 - self.width // 2, 720 // 2 - self.height // 2)
            self.huge_sprite = pygame.transform.scale(assets.dialogue("dialogue_1.png"), (self.width, self.height))
            self.__sprite = self.attach_component(
                (KelvinSprite(self.huge_sprite, (self.position.x, self.position.y), layer=500)))
            self.ending = True

        self.crystal_timer -= game.delta_time

        if self.ending:
            if ((pygame.mouse.get_pressed()[0]) or game.input.is_key_down(pygame.K_SPACE)) and self.click_allowed <= 0:
                self.click_allowed = 0.1
                if self.i == 4:
                    game.time_factor = game.event.time_factor_backup
                    game.world.get_single_entity(main.CoinSpawner).paused = False
                    level.add_level()
                    self.destroy()

                else:
                    self.__sprite.image = pygame.transform.scale(assets.dialogue(f"dialogue_{self.i}.png"),
                                                                 (self.width, self.height))
                    self.__sprite.dirty = 1
                    self.i += 1
            self.click_allowed -= 0.001
