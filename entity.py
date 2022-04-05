from abc import ABC


class Entity(ABC):
    def render(self, screen):
        pass

    def take_event(self, event):
        pass