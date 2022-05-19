from typing import List

import pygame

from kelvin452.engine.systems.base import System


class EventSystem(System):
    __slots__ = ("continue_running", "__pressed_keys", "frame_events")

    def __init__(self):
        super().__init__()
        self.continue_running = True
        self.__pressed_keys = []
        self.frame_events: List[pygame.event.Event] = []

    def process_events(self):
        self.__pressed_keys = pygame.key.get_pressed()
        self.frame_events.clear()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.continue_running = False
                return
            self.frame_events.append(event)
