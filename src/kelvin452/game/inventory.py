import pygame

from kelvin452.engine.fonts import default_font
from kelvin452.engine import *


class Inventory(Entity, EventConsumer):
    def __init__(self, x=1204, y=62):
        super().__init__()
        self.position = Vector2(x, y)
        self.height = 50
        self.width = 50
        self.huge_inventory_sprite = pygame.transform.scale(assets.sprite("inventory.png"), (self.width, self.height))
        self.__sprite = self.attach_component(
            KelvinSprite(self.huge_inventory_sprite, (self.position.x, self.position.y), layer=300))

    def consume_event(self, new_event: pygame.event.Event) -> bool:
        if new_event.type == pygame.MOUSEBUTTONDOWN \
                and self.__sprite.rect.collidepoint(game.input.get_mouse_position()):
            self.open_menu()
            return True
        return False

    def open_menu(self):
        ...


class InventoryMenu(Entity, EventConsumer):
    def __init__(self):
        super().__init__()
        self.background = self.attach_component(Image(assets.ui("inventory_menu.png")))
        self.background.position = (game.viewport - self.background.size) / 2
