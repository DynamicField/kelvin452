from typing import List, Set

import pygame

from kelvin452.engine.game import game
from kelvin452.engine.systems.base import System
from kelvin452.engine.systems.world import HasLifetime, Component


class EventConsumer(HasLifetime):
    def __init__(self):
        super().__init__()
        self.attach_component(EventNotifyComponent())

    def consume_event(self, new_event: pygame.event.Event) -> bool:
        return False

    def get_priority(self):
        return 0


class EventNotifyComponent(Component):
    def __init__(self):
        super().__init__()

    def _attached(self, attached_to):
        game.event.event_consumers.add(attached_to)

    def _destroyed(self):
        game.event.event_consumers.discard(self._attached_to)


class EventSystem(System):
    __slots__ = ("continue_running", "frame_events")

    def __init__(self):
        super().__init__()
        self.time_factor_backup = game.time_factor
        self.continue_running = True
        self.frame_events: List[pygame.event.Event] = []
        self.event_consumers: Set[EventConsumer] = set()

    def process_events(self):
        self.frame_events.clear()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.continue_running = False
                return
            event_consumed = self.consume_event_for_entities(event)
            if not event_consumed and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game.time_factor != 0:
                        self.time_factor_backup = game.time_factor
                        game.time_factor = 0
                    else:
                        game.time_factor = self.time_factor_backup

            self.frame_events.append(event)

    def consume_event_for_entities(self, event: pygame.event.Event):
        consumers: List[EventConsumer] = list(self.event_consumers)
        consumers.sort(key=lambda x: x.get_priority(), reverse=True)
        for cons in consumers:
            if cons.consume_event(event):
                return True
        return False

