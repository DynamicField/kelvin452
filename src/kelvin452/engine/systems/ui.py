from typing import Optional, List, Callable, TypeVar, Generic

import pygame
from pygame import Vector2

import kelvin452.engine.fonts as fonts
from kelvin452.engine.game import game
from kelvin452.engine.systems.base import Component
from kelvin452.engine.systems.ticking import TickOrder
from kelvin452.engine.systems.rendering import KelvinSprite, EMPTY_SURFACE, RenderingGroup


class UIElement(Component):
    def __init__(self):
        super().__init__()
        self.governor: Optional[UIElement] = None
        self.governed_elements: List[UIElement] = []
        self.__last_pos = Vector2(0, 0)
        self.__position = Vector2(0, 0)
        self.dirty = True
        game.ticking.add_tick_function(lambda: self._tick(), TickOrder.POST_ENTITY).attach_to(self)

    @property
    def position(self):
        return self.__position

    @position.setter
    def position(self, value):
        if self.__position is not value:
            self.__position = value
            self.dirty = True

    @property
    def size(self):
        return self._get_size()

    @size.setter
    def size(self, value: Vector2):
        self._set_size(value)

    def _get_size(self) -> Vector2:
        return Vector2(1, 1)

    def _set_size(self, value: Vector2):
        pass

    U = TypeVar('U', bound='UIElement')

    def govern(self, other: U) -> U:
        other.governor = self
        self.governed_elements.append(other)
        self.attach_component(other)
        return other

    def release_governed(self, other: 'UIElement'):
        if other in self.governed_elements:
            other.governor = None
            self.governed_elements.remove(other)
            self.detach_component(other)
            self._governed_element_removed(other)

    def _component_detached(self, component: 'Component'):
        if isinstance(component, UIElement) and component in self.governed_elements:
            if self.is_alive:
                self.release_governed(component)
            else:
                self.governed_elements.remove(component)
                component.governor = None

    def _governed_element_removed(self, element: 'UIElement'):
        pass

    def update_depth(self, layer=0):
        self._change_layer(layer)
        for element in self.governed_elements:
            element.update_depth(layer + 1)

    def _change_layer(self, layer: int):
        pass

    def _tick(self):
        if self.governor is None:
            self.update_depth()
        self._update_dirty_state()
        self.dirty = False

    def _update_dirty_state(self):
        if self.__last_pos != self.position:
            self.dirty = True
            self.__last_pos = self.position


class TextBlock(UIElement):
    def __init__(self, text="", font=fonts.default_font, color=(255, 255, 255), background=None):
        super().__init__()
        self.sprite = self.attach_component(
            KelvinSprite(EMPTY_SURFACE, auto_update=False, group=RenderingGroup.UI))

        self.__text = text
        self.__font = font
        self.__color = color
        self.__background = background
        self.image_dirty = True
        self._update_dirty_state()

    @property
    def text(self):
        return self.__text

    @text.setter
    def text(self, value):
        value = str(value)  # Convertir en string
        if value != self.__text:
            self.__text = value
            self.image_dirty = True

    @property
    def font(self):
        return self.__font

    @font.setter
    def font(self, value):
        if value != self.__font:
            self.__font = value
            self.image_dirty = True

    @property
    def color(self):
        return self.__color

    @color.setter
    def color(self, value):
        if value != self.__color:
            self.__color = value
            self.image_dirty = True

    @property
    def background(self):
        return self.__background

    @background.setter
    def background(self, value):
        if value != self.__background:
            self.__background = value
            self.image_dirty = True

    def _get_size(self):
        return Vector2(self.sprite.image.get_size())

    def _change_layer(self, layer):
        if self.sprite.layer != layer:
            self.sprite.change_layer(layer)

    def force_update(self):
        self.dirty = True
        self.image_dirty = True
        self._update_dirty_state()

    def _update_dirty_state(self):
        super()._update_dirty_state()
        if self.dirty:
            self.sprite.position = self.position

        if self.image_dirty:
            self.sprite.image = self.__font.render(self.text,
                                                   True,
                                                   self.color,
                                                   self.background)
            self.sprite.dirty = 1
            self.image_dirty = False


U = TypeVar('U', bound=UIElement)


class Button(UIElement, Generic[U]):
    def __init__(self, size: Vector2, background: pygame.Surface, child: Optional[U]):
        super().__init__()
        self.__background_image = background
        self.__background_sprite = self.attach_component(
            KelvinSprite(pygame.transform.scale(background, size), group=RenderingGroup.UI))
        self.image_dirty = False
        self.child = child
        self.__last_size = size
        self.__size = size
        self.on_click: Optional[Callable] = None
        self.click_hold = False
        if child is not None:
            self.govern(child)

    @property
    def background(self):
        return self.__background_image

    @background.setter
    def background(self, value):
        if self.__background_image != value:
            self.__background_image = value
            self.dirty = True
            self.image_dirty = True

    def _get_size(self):
        return self.__size

    def _set_size(self, value: Vector2):
        if self.__size != value and self.governor is None:
            self.__size = value
            self.dirty = True

    def _update_dirty_state(self):
        super()._update_dirty_state()
        if self.__last_size != self.__size:
            self.dirty = True
            self.__last_size = self.__size
        if self.dirty:
            # Mettre la bonne taille
            if self.__background_sprite.image.get_size() != self.__size or self.image_dirty:
                self.__background_sprite.image = pygame.transform.scale(self.__background_image, self.__size)
                self.__background_sprite.dirty = 1
                self.image_dirty = False

            self.__background_sprite.position = self.position

        # Peut-être que le contenu a changé
        if self.child is not None:
            size_diff = (self.__size - self.child.size)
            size_diff.xy = max(size_diff.x, 0), max(size_diff.y, 0)
            self.child.position = self.position + size_diff / 2
            self.child._update_dirty_state()

    def _change_layer(self, layer):
        if self.__background_sprite.layer != layer:
            self.__background_sprite.change_layer(layer)

    def _governed_element_removed(self, element: 'UIElement'):
        if element == self.child:
            self.child = None

    def _tick(self):
        super()._tick()
        if self.on_click is not None:
            hit_rect = pygame.Rect(self.position, self.size)
            if hit_rect.collidepoint(game.input.get_mouse_position()):
                if game.input.is_mouse_left_click_down():
                    self.click_hold = True
                elif self.click_hold:  # Relâché
                    self.click_hold = False
                    self.on_click()
            elif not game.input.is_mouse_left_click_down():
                self.click_hold = False


class Image(UIElement):
    def __init__(self, image: pygame.Surface, size: Optional[Vector2] = None):
        super().__init__()
        self.__image = image
        self.__sprite = self.attach_component(KelvinSprite(image, group=RenderingGroup.UI))
        self.__size = size
        self.__last_size = size
        self._update_dirty_state()

    def _get_size(self):
        val = self.__size if self.__size is not None else self.__image.get_size()
        return Vector2(val)

    def _set_size(self, value: Vector2):
        if self.__size != value:
            self.__size = value
            self.dirty = True

    def _change_layer(self, layer: int):
        if self.__sprite.layer != layer:
            self.__sprite.change_layer(layer)

    def _update_dirty_state(self):
        super()._update_dirty_state()
        if self.__last_size != self.__size:
            self.dirty = True
            self.__last_size = self.__size
        if self.dirty:
            self.__sprite.position = self.position
            if self.__sprite.image.get_size() != self.size:
                self.__sprite.image = pygame.transform.scale(self.__image, self.size)
                self.__background_sprite.dirty = 1
