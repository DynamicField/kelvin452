from typing import *


class HasLifetime:
    def __init__(self):
        self.__components = set()
        self.__is_alive = True
        super().__init__()

    @property
    def is_alive(self):
        return self.__is_alive

    def _report_destroyed(self):
        self.__is_alive = False
        for component in list(self.__components):
            component.destroy()

    @property
    def components(self) -> Iterable['Component']:
        return self.__components

    C = TypeVar('C', bound='Component')

    def get_component(self, comp_type: Type[C]) -> Optional[C]:
        for component in self.__components:
            if isinstance(component, comp_type):
                return component
        return None

    def attach_component(self, component: C) -> C:
        assert self.is_alive, "The entity/system must be alive."
        if component not in self.__components:
            self.__components.add(component)
            component.destroyed_notifiers.append(lambda: self.__on_component_destroyed(component))
        return component

    def __on_component_destroyed(self, component: 'Component'):
        if self.is_alive:
            self.__components.remove(component)


class Component:
    def __init__(self):
        self.__is_destroyed = False
        self.destroyed_notifiers: List[Optional[Callable]] = []

    def _destroyed(self):
        pass

    def destroy(self):
        if not self.__is_destroyed:
            self.__is_destroyed = True
            self._destroyed()

    def attach_to(self, target: HasLifetime):
        target.attach_component(self)


class System(HasLifetime):
    def __init__(self):
        super().__init__()

    def _started(self):
        pass

    def start(self):
        print(f"System {type(self)} started")
        self._started()

    def _stopped(self):
        pass

    def stop(self):
        print(f"System {type(self)} stopped")
        self._report_destroyed()
        self._stopped()
