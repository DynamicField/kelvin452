import collections
from typing import *

import pygame.draw
from pygame import Rect, Vector2
from math import sqrt
from math import fabs

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

    def closet_point(self, center, rect):  # it returns the coordinate of rect point closest to the center of the circle
        # the reference is A, it means if the function return (1,5), the point is at rect.x + 1, rect.y+5

        dic = {
            'a': (0, 0),
            'b': (rect.width, 0),
            'c': (0, rect.height),
            'd': (rect.width, rect.height)
        }
        center_value = center.x + center.y
        min = 'a'  # index of the littlest
        for i in dic:
            if fabs(dic[i][0] + dic[i][1] - center_value) < fabs(dic[min][0] + dic[min][1] - center_value):
                min = i

        return dic[min]

    def refresh_collisions(self):
        self.__refreshing_collisions = True

        # Bruteforce, faudrait optimiser ça avec des quadtrees.
        for hit_box in self.__refreshed_hit_boxes.copy():
            for other_hit_box in self.__all_hitboxes.copy():
                if hit_box.is_destroyed or other_hit_box.is_destroyed or hit_box == other_hit_box:
                    continue
                if hit_box.type == 1:
                    if other_hit_box.type == 1:
                        if hit_box.rect.colliderect(other_hit_box.rect):
                            self.on_collide(hit_box, other_hit_box)
                        elif len(hit_box.ongoing_collisions) > 0:
                            self.clear_ongoing_collisions(hit_box, other_hit_box)
                    elif other_hit_box.type == 2:
                        dx = sqrt((hit_box.rect.x + hit_box.rect.width
                                   / 2 - other_hit_box.attached_entity.center_position.x) ** 2)
                        dy = sqrt((hit_box.rect.y + hit_box.rect.height
                                   / 2 - other_hit_box.attached_entity.center_position.y) ** 2)
                        if (dx <= other_hit_box.circle + hit_box.rect.width) and \
                                (dy <= other_hit_box.circle + hit_box.rect.height):
                            if ((other_hit_box.attached_entity.center_position.x - other_hit_box.circle
                                 < (hit_box.rect.x - 1)
                                 < other_hit_box.attached_entity.center_position.x + other_hit_box.circle)
                                or (other_hit_box.attached_entity.center_position.x - other_hit_box.circle
                                    < (hit_box.rect.x + 1)
                                    < other_hit_box.attached_entity.center_position.x + other_hit_box.circle)) \
                                    and ((other_hit_box.attached_entity.center_position.y - other_hit_box.circle
                                          < (hit_box.rect.y - 1)
                                          < other_hit_box.attached_entity.center_position.y + other_hit_box.circle)
                                         or (other_hit_box.attached_entity.center_position.y - other_hit_box.circle
                                             < (hit_box.rect.y + 1)
                                             < other_hit_box.attached_entity.center_position.y + other_hit_box.circle)):
                                # it's : if ((xa-r < xb-1 < xa + r ) or (xa -r<xb+1<xa + r))
                                # and ((ya-r < yb-1 < ya + r ) or (ya -r<yb+1<ya + r))
                                self.on_collide(hit_box, other_hit_box)
                            elif len(hit_box.ongoing_collisions) > 0:
                                self.clear_ongoing_collisions(hit_box, other_hit_box)
                elif hit_box.type == 2:
                    if other_hit_box.type == 1:
                        dx = sqrt((other_hit_box.rect.x + other_hit_box.rect.width
                                   / 2 - hit_box.attached_entity.center_position.x) ** 2)
                        dy = sqrt((other_hit_box.rect.y + other_hit_box.rect.height
                                   / 2 - hit_box.attached_entity.center_position.y) ** 2)
                        if (dx <= hit_box.circle + other_hit_box.rect.width) \
                                and (dy <= hit_box.circle + other_hit_box.rect.height):
                            if ((hit_box.attached_entity.center_position.x - hit_box.circle
                                 < (other_hit_box.rect.x - 1)
                                 < hit_box.attached_entity.center_position.x + hit_box.circle)
                                or (hit_box.attached_entity.center_position.x - hit_box.circle
                                    < (other_hit_box.rect.x + 1)
                                    < hit_box.attached_entity.center_position.x + hit_box.circle)) \
                                    and ((hit_box.attached_entity.center_position.y - hit_box.circle
                                          < (other_hit_box.rect.y - 1)
                                          < hit_box.attached_entity.center_position.y + hit_box.circle)
                                         or (hit_box.attached_entity.center_position.y - hit_box.circle
                                             < (other_hit_box.rect.y + 1)
                                             < hit_box.attached_entity.center_position.y + hit_box.circle)):

                                self.on_collide(hit_box, other_hit_box)
                            elif len(hit_box.ongoing_collisions) > 0:
                                self.clear_ongoing_collisions(hit_box, other_hit_box)
                    elif other_hit_box.type == 2:
                        dx = hit_box.attached_entity.center_position.x - other_hit_box.attached_entity.position.x / 2
                        dy = hit_box.attached_entity.center_position.y - other_hit_box.attached_entity.position.y / 2
                        distance = sqrt(dx ** 2 + dy ** 2)
                        if distance < hit_box.circle + other_hit_box.circle:
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
        self.__pending_removals.clear()


class CollisionHitBox(EntityComponent):
    """
    Une hit box de collision, qui envoie une notification lorsqu’une autre
    hit box est touchée.
    """

    __slots__ = ("__follow_sprite_rect", "__rect", "__rect_set", "ongoing_collisions", "draw_box", "margin")

    def __init__(self, follow_sprite_rect: bool, draw_box=False, offset: pygame.Rect = pygame.Rect(0, 0, 0, 0),
                 type=1, radius=1):
        """
        Crée une nouvelle hit box, ne pas oublier d'attacher le composant avec
        ``self.attach_component(...)`` !!

        :param follow_sprite_rect: Si la hit box doit être la même que celle du sprite.
        :param draw_box: Si une boite rouge doit être dessinée pour représenter la hitbox (debug).
        :param offset: La marge de la hit box
        """
        super().__init__()
        self.__follow_sprite_rect = follow_sprite_rect
        self.__rect = Rect(0, 0, 0, 0)
        self.__rect_set = False
        self.circle = radius
        self.type = type  # type of the hitbox, 1 -> rect, 2 -> circle
        self.ongoing_collisions: Set['CollisionHitBox'] = set()
        self.draw_box = draw_box
        self.offset = offset

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
            if sprite is not None:
                adjusted_rect = sprite.rect.move(self.offset.x, self.offset.y)
                adjusted_rect.width = self.offset.width
                adjusted_rect.height = self.offset.height
                self.rect = adjusted_rect
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
        if self.type == 1:
            pygame.draw.rect(pygame.display.get_surface(), color, self.rect, 2)
        if self.type == 2:
            pygame.draw.circle(pygame.display.get_surface(), color,
                               (self.attached_entity.center_position.x, self.attached_entity.center_position.y),
                               self.circle, 2)


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
