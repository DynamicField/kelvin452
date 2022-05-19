import collections
from enum import Enum, auto
from typing import *

from kelvin452.engine.systems.base import System, Component


class TickOrder(Enum):
    ENTITY = auto()
    COLLIDE = auto()
    POST_RENDER = auto()


class TickEntry(Component):
    __slots__ = ("order", "function", "removal_pending")

    def __init__(self, order: TickOrder, function: Callable):
        super().__init__()
        self.order = order
        self.function = function
        self.removal_pending = False

    def remove(self):
        self.destroy()

    def _destroyed(self):
        self.removal_pending = True


class TickingSystem(System):
    def __init__(self):
        super().__init__()
        self.__tick_functions: Dict[TickOrder, List[TickEntry]] = collections.defaultdict(list)

    def add_tick_function(self, function: Callable, order: TickOrder) -> TickEntry:
        entry = TickEntry(order, function)
        self.__tick_functions[order].append(entry)
        return entry

    def run_ticks(self, order: TickOrder):
        i = 0
        tick_functions = self.__tick_functions[order]
        while i < len(tick_functions):
            entry = tick_functions[i]
            if entry.removal_pending:
                tick_functions.pop(i)
            else:
                entry.function()
                i += 1
