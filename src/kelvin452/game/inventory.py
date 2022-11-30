import pygame

from kelvin452.engine.fonts import default_font
from kelvin452.engine import *
import kelvin452.game.__main__ as main


class Inventory(Entity, EventConsumer):
    def __init__(self, x=1204, y=62):
        super().__init__()
        self.content = []
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
        def unpause():
            game.time_factor = game.event.time_factor_backup

        menu = InventoryMenu(self)
        menu.destroyed_notifiers.append(unpause)
        game.world.spawn_entity(menu)

    def add_inventory(self, object: Entity):
        self.content.append(object)

    def remove_inventory(self, object: Entity):
        for i in range(len(self.content)):
            if self.content[i] == object:
                self.content.pop(i)

    def is_in_inventory(self, object: Entity):
        for i in self.content:
            if i == object:
                return True
        return False


def _make_filled_surface(dimensions, color):
    surface = pygame.Surface(dimensions)
    surface.fill(color)
    return surface


class InventoryMenu(Entity, EventConsumer):
    BUY_BUTTON_SIZE = Vector2(210, 100)
    RED_BUTTON_SURFACE = _make_filled_surface(BUY_BUTTON_SIZE, (220, 30, 0))
    HEADER_FONT = pygame.font.SysFont(pygame.font.get_default_font(), 40)

    def __init__(self, inventory):
        super().__init__()
        self.inventory = inventory
        game.time_factor = 0
        self.background = self.attach_component(Image(assets.ui("inventory_menu.png")))
        self.background.position = (game.viewport - self.background.size) / 2

        self.inventory_text = self.background.govern(TextBlock("INVENTORY", font=InventoryMenu.HEADER_FONT))
        self.place_element_centered(self.inventory_text, 30)

        self.close_button = self.background.govern(
            Button(Vector2(160, 50),
                   InventoryMenu.RED_BUTTON_SURFACE,
                   TextBlock("FERMER")))
        self.close_button.on_click = lambda: self.cleaner()
        self.place_element_centered(self.close_button, self.background.size.y - 100)
        self.placement()

    def place_element_centered(self, target, y):
        target.position.x = self.background.position.x + (self.background.size.x - target.size.x) / 2
        target.position.y = self.background.position.y + y

    def consume_event(self, new_event: pygame.event.Event) -> bool:
        if new_event.type == pygame.MOUSEBUTTONDOWN:
            return True
        if new_event.type == pygame.KEYDOWN:
            if new_event.key == pygame.K_ESCAPE:
                self.cleaner()
                return True
        return False

    def placement(self):  # it will take all the objects in inventory.content and put it in the menu
        x = 329
        y = 217
        size = 31 * 3
        while ((size + 1) * len(self.inventory.content) - 1) > \
                ((950 - 329) * (((437 - 217) + 1) // (size + 1))):
            size -= 1
        print(size)

        for i in range(len(self.inventory.content)):
            game.world.spawn_entity(self.inventory.content[i](x, y, size))
            if x + 2 * (1 + size) > 950:
                x = 329
                y += 1 + size
            else:
                x += 1 + size

    def cleaner(self):
        for i in self.inventory.content:
            for j in game.world.get_entities(i):
                j.destroy()
        self.destroy()


class PiercingCrystalEntity(Entity):
    def __init__(self, x, y, size=31):
        super().__init__()
        self.position = Vector2(x, y)
        self.size = (size * 31) / 31
        self.huge_piercingcrystal_sprite = pygame.transform.scale(assets.sprite("piercing_crystal.png"), (size, size))
        self.__sprite = self.attach_component(
            KelvinSprite(self.huge_piercingcrystal_sprite, (self.position.x, self.position.y), layer=500))
