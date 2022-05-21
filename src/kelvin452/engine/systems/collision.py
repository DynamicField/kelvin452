import collections
from typing import *

import pygame.draw
from pygame import Rect, Vector2

from kelvin452.engine.game import game
from kelvin452.engine.systems.base import System, Component
from kelvin452.engine.systems.rendering import KelvinSprite
from kelvin452.engine.systems.ticking import TickOrder
from kelvin452.engine.systems.world import EntityComponent, Entity


class CollisionSystem(System):
    def __init__(self):
        super().__init__()
        self.__refreshed_hit_boxes: Set['CollisionHitBox'] = set()
        self.__all_hitboxes: Set['CollisionHitBox'] = set()
        self.__refreshing_collisions = False
        self.__pending_removals: List['CollisionHitBox'] = []

    def report_hit_box_added(self, hit_box: 'CollisionHitBox'):
        self.__all_hitboxes.add(hit_box)
        self.__refreshed_hit_boxes.add(hit_box)

    def report_hit_box_destroyed(self, hit_box: 'CollisionHitBox'):
        self.__pending_removals.append(hit_box)
        if not self.__refreshing_collisions:
            self.remove_pending_hit_boxes()

    def refresh_hit_box(self, hit_box: 'CollisionHitBox'):
        self.__refreshed_hit_boxes.add(hit_box)

    def refresh_collisions(self):
        self.__refreshing_collisions = True

        # Bruteforce, faudrait optimiser ça avec des quadtrees.
        for hit_box in self.__refreshed_hit_boxes:
            for other_hit_box in self.__all_hitboxes:
                if hit_box.is_destroyed or other_hit_box.is_destroyed or hit_box == other_hit_box:
                    continue
                if hit_box.rect.colliderect(other_hit_box.rect):
                    self.on_collide(hit_box, other_hit_box)
                elif len(hit_box.ongoing_collisions) > 0:
                    self.clear_ongoing_collisions(hit_box, other_hit_box)

        self.__refreshed_hit_boxes.clear()
        # On retire toutes les hitbox après pour éviter des conflits
        # avec les listes.
        self.remove_pending_hit_boxes()

        self.__refreshing_collisions = False

    @staticmethod
    def on_collide(hit_box: 'CollisionHitBox', other_hit_box: 'CollisionHitBox'):
        if other_hit_box in hit_box.ongoing_collisions:
            return  # On fait rien

        hit_box.ongoing_collisions.add(other_hit_box)
        other_hit_box.ongoing_collisions.add(hit_box)

        hit_box.notify_collision(other_hit_box)
        other_hit_box.notify_collision(hit_box)

    @staticmethod
    def clear_ongoing_collisions(hit_box: 'CollisionHitBox', other_hit_box: 'CollisionHitBox'):
        hit_box.ongoing_collisions.discard(other_hit_box)
        other_hit_box.ongoing_collisions.discard(hit_box)

    def remove_pending_hit_boxes(self):
        for hit_box in self.__pending_removals:
            self.__all_hitboxes.discard(hit_box)
            self.__refreshed_hit_boxes.discard(hit_box)
            # Aussi supprimer les collisions en cours
            for other_hit_box in list(hit_box.ongoing_collisions):
                self.clear_ongoing_collisions(hit_box, other_hit_box)
            print("boom!")
        self.__pending_removals.clear()


class CollisionHitBox(EntityComponent):
    """
    Une hit box de collision, qui envoie une notification lorsqu’une autre
    hit box est touchée.
    """

    __slots__ = ("__follow_sprite_rect", "__rect", "__rect_set", "ongoing_collisions", "draw_box", "margin")

    def __init__(self, follow_sprite_rect: bool, draw_box=False, margin: Vector2 = Vector2(0, 0)):
        """
        Crée une nouvelle hit box, ne pas oublier d'attacher le composant avec
        ``self.attach_component(...)`` !!

        :param follow_sprite_rect: Si la hit box doit être la même que celle du sprite.
        :param draw_box: Si une boite rouge doit être dessinée pour représenter la hitbox (debug).
        :param margin: La marge de taille du sprite (largeur, hauteur)
        """
        super().__init__()
        self.__follow_sprite_rect = follow_sprite_rect
        self.__rect = Rect(0, 0, 0, 0)
        self.__rect_set = False
        self.ongoing_collisions: Set['CollisionHitBox'] = set()
        self.draw_box = draw_box
        self.margin = margin

    @property
    def rect(self) -> Rect:
        return self.__rect

    @rect.setter
    def rect(self, value: Rect):
        self.__rect = value
        self.__rect_set = True

    def _entity_tick(self, entity: Entity):
        if self.__follow_sprite_rect and not self.__rect_set:
            sprite = entity.get_component(KelvinSprite)
            if sprite is not None and sprite.rect != self.rect:
                self.rect = sprite.rect.inflate(*self.margin)
        if self.__rect_set:
            game.collision.refresh_hit_box(self)
            self.__rect_set = False
        if self.draw_box:
            game.renderer.queue_rendering_action(lambda: self.draw_debug_box())

    def react_on_collide(self, callback: Callable[[Entity], None]):
        self.attach_component(CollisionListener(callback)).attach_to(self.attached_entity)

    def notify_collision(self, other: 'CollisionHitBox'):
        if isinstance(self.attached_entity, ReactsToCollisions):
            self.attached_entity.notify_on_collide(other.attached_entity)
        for component in self.components:
            if isinstance(component, CollisionListener):
                component.call(other.attached_entity)

    def _attached(self, attached_to: Entity):
        game.collision.report_hit_box_added(self)

    def _destroyed(self):
        game.collision.report_hit_box_destroyed(self)

    def draw_debug_box(self):
        # Rouge = normal
        # Violet = collision
        color = (255, 0, 0) if len(self.ongoing_collisions) == 0 else (128, 0, 128)
        pygame.draw.rect(pygame.display.get_surface(), color, self.rect, 2)


class CollisionListener(Component):
    def __init__(self, callback: Callable[[Entity], None]):
        super().__init__()
        self.callback = callback

    def call(self, collided_with: Entity):
        self.callback(collided_with)


class ReactsToCollisions:
    def _on_collide(self, other: Entity):
        pass

    def notify_on_collide(self, other: Entity):
        self._on_collide(other)
