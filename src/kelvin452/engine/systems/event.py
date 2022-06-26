from typing import List

import pygame

from kelvin452.engine.game import game
from kelvin452.engine.systems.base import System


class EventConsumer:
    def consume_event(self, new_event: pygame.event.Event) -> bool:
        return False

    def get_priority(self):
        return 0


def consume_event_for_entities(event: pygame.event.Event):
    entities: List[EventConsumer] = game.world.get_entities(EventConsumer)
    entities.sort(key=lambda x: x.get_priority(), reverse=True)
    for entity in entities:
        if entity.consume_event(event):
            return True
    return False


class EventSystem(System):
    __slots__ = ("continue_running", "frame_events")

    def __init__(self):
        super().__init__()
        self.time_factor_backup = game.time_factor
        self.continue_running = True
        self.frame_events: List[pygame.event.Event] = []

    def process_events(self):
        self.frame_events.clear()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.continue_running = False
                return
            event_consumed = consume_event_for_entities(event)
            if not event_consumed and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game.time_factor != 0:
                        self.time_factor_backup = game.time_factor
                        game.time_factor = 0
                    else:
                        game.time_factor = self.time_factor_backup

            self.frame_events.append(event)
