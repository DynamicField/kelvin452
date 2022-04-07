import pygame
from typing import *
from game import game


class WorldSystem:
    def __init__(self):
        self.entities: List[Entity] = []

    def spawn_entity(self, entity: 'Entity'):
        assert entity not in self.entities, "Entity already spawned"
        self.entities.append(entity)
        entity.notify_spawned()

    def destroy_entity(self, entity: 'Entity'):
        assert entity in self.entities, "Entity not found"
        self.entities.remove(entity)
        entity.notify_destroyed()

    def tick(self):
        for entity in self.entities:
            entity.notify_tick()


class Entity:
    def __init__(self):
        self.__sprites = []
        self._is_destroyed = False

    def _spawned(self):
        pass

    def _destroyed(self):
        pass

    def _tick(self):
        pass

    def notify_spawned(self):
        self._spawned()

    def notify_destroyed(self):
        self._is_destroyed = True
        for sprite in self.__sprites:
            sprite.kill()
        self._destroyed()

    def notify_tick(self):
        self._tick()

    @property
    def is_destroyed(self):
        return self._is_destroyed

    def show_sprite(self, sprite: pygame.sprite.DirtySprite):
        game.renderer.add_sprite(sprite)
        self.__sprites.append(sprite)
