from functools import cached_property
from typing import Tuple
import pygame


class RenderingSystem:
    def __init__(self):
        self._sprites = pygame.sprite.LayeredDirty()

    def render(self, screen: pygame.Surface):
        self._sprites.clear(screen, self._background)
        updated_region = self._sprites.draw(screen)
        pygame.display.update(updated_region)

    @cached_property
    def _background(self):
        surface = pygame.surface.Surface((1280, 720))
        surface.fill((50, 0, 0))
        return surface

    def add_sprite(self, sprite: pygame.sprite.Sprite):
        self._sprites.add(sprite)

    def remove_sprite(self, sprite: pygame.sprite.Sprite):
        self._sprites.remove(sprite)


def make_sprite(image: pygame.surface.Surface, location: Tuple[float, float]) -> pygame.sprite.DirtySprite:
    sprite = pygame.sprite.DirtySprite()
    sprite.image = image
    sprite.rect = image.get_rect().move(*location)
    return sprite
