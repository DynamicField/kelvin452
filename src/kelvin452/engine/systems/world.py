import pygame
from typing import *

from pygame import Vector2

from kelvin452.engine.game import game
import inspect
import collections

from kelvin452.engine.systems.base import System, HasLifetime, Component
from kelvin452.engine.systems.ticking import TickOrder, TickEntry


class WorldSystem(System):
    def __init__(self):
        super().__init__()
        self.entities: List[Entity] = []
        self.__entities_per_type: Dict[type, List[Entity]] = collections.defaultdict(list)

    def spawn_entity(self, entity: 'Entity'):
        assert entity not in self.entities, "Entity already spawned"
        self.entities.append(entity)
        for parent_type in inspect.getmro(type(entity)):
            self.__entities_per_type[parent_type].append(entity)
        entity.notify_spawned()

    def destroy_entity(self, entity: 'Entity'):
        assert entity in self.entities, "Entity not found"
        self.entities.remove(entity)
        for parent_type in inspect.getmro(type(entity)):
            self.__entities_per_type[parent_type].remove(entity)
        entity.notify_destroyed()

    T = TypeVar('T', bound='Entity')

    def get_entities(self, type_filter: Type[T] = None) -> Iterable[T]:
        if filter is not None:
            return self.__entities_per_type[type_filter]
        return self.entities

    def get_single_entity(self, type_filter: Type[T]) -> Optional[T]:
        filtered = self.__entities_per_type[type_filter]

        assert len(filtered) <= 1, "Il y a plus de deux entités de ce type"
        if len(filtered) == 1:
            return filtered[0]
        else:
            return None


class Entity(HasLifetime):
    """
    La classe de base pour les entités. Une entité est quelque chose
    qui existe, physiquement ou non, dans le jeu.

    Elle peut être spawn en utilisant ``game.world.spawn_entity(mon_entité)``.
    """
    next_id = 0

    def __init__(self):
        """
        Crée une nouvelle entité
        """
        self.__tick_function: Optional[TickEntry] = None
        self.__position = Vector2(0, 0)
        self.id = Entity.next_id
        Entity.next_id += 1
        super().__init__()

    def _spawned(self):
        """
        Appelée quand l'entité vient d'être spawn dans le jeu.
        """
        pass

    def _destroyed(self):
        """
        Appelée quand l'entité vient d'être détruite dans le jeu.
        """
        pass

    def _tick(self):
        """
        Appelée à chaque frame du jeu. Il est possible d'utiliser
        ``game.delta_time`` pour obtenir la durée de la frame précédente
        afin d'avoir un référentiel de temps.
        """
        pass

    @property
    def position(self):
        return self.__position

    @position.setter
    def position(self, new_pos: Union[Vector2, Tuple[float, float]]):
        self.__position = Vector2(new_pos)

    def notify_spawned(self):
        def run_tick():
            self._tick()
            for component in self.components:
                if isinstance(component, EntityComponent):
                    component.notify_entity_tick(self)

        game.ticking.add_tick_function(run_tick, TickOrder.ENTITY).attach_to(self)
        self._spawned()

    def notify_destroyed(self):
        self._report_destroyed()
        if self.__tick_function is not None:
            self.__tick_function.remove()
        self._destroyed()

    def destroy(self):
        if self.is_alive:
            game.world.destroy_entity(self)

    def show_sprite(self, sprite: pygame.sprite.DirtySprite):
        game.renderer.add_sprite(sprite)

    def __repr__(self):
        return f"{type(self).__name__}{self.id}"


class EntityComponent(Component):
    def __init__(self):
        super().__init__()
        self.attached_entity: Entity = cast(Any, None)

    def _entity_tick(self, entity: Entity):
        pass

    def notify_entity_tick(self, entity: Entity):
        if not self.is_destroyed:
            self._entity_tick(entity)

    def _attached(self, attached_to: Entity):
        pass

    def report_attachment(self, target: HasLifetime):
        assert isinstance(target, Entity), f"Can't attach a component of type {type(self)} to a non-entity."
        self.attached_entity = target
        super().report_attachment(target)
