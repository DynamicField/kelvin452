from typing import *


class HasLifetime:
    def __init__(self):
        self.__components = set()
        self.__is_alive = True
        self.destroyed_notifiers: List[Callable] = []
        self.attached_listeners: Dict[HasLifetime, Callable] = {}
        super().__init__()

    @property
    def is_alive(self):
        return self.__is_alive

    def _report_destroyed(self):
        self.__is_alive = False
        print("Destroying " + str(self))
        for notifier in self.destroyed_notifiers:
            notifier()
        for component in list(self.__components):
            component.destroy()

    @property
    def components(self) -> Iterable['Component']:
        return self.__components

    def _component_attached(self, component: 'Component'):
        pass

    def _component_detached(self, component: 'Component'):
        pass

    C = TypeVar('C', bound='Component')

    def get_component(self, comp_type: Type[C]) -> Optional[C]:
        for component in self.__components:
            if isinstance(component, comp_type):
                return component
        return None

    def attach_component(self, component: C) -> C:
        assert self.is_alive, "The entity/system must be alive."
        assert not component.is_destroyed, "The component must be alive."
        if component not in self.__components:
            self.__components.add(component)
            self.attached_listeners[component] = lambda: self.__on_component_destroyed(component)
            component.destroyed_notifiers.append(self.attached_listeners[component])
            component.report_attachment(self)
            self._component_attached(component)
        return component

    def detach_component(self, component: 'Component'):
        assert self.is_alive, "The entity/system must be alive."
        if component in self.__components:
            self.__components.remove(component)
            component.destroyed_notifiers.remove(self.attached_listeners[component])
            del self.attached_listeners[component]

            component.report_detachment()
            self._component_detached(component)

    def __on_component_destroyed(self, component: 'Component'):
        if self.is_alive:
            self.detach_component(component)


class Component(HasLifetime):
    def __init__(self):
        super().__init__()
        self._attached_to = None

    @property
    def is_destroyed(self):
        return not self.is_alive

    def _destroyed(self):
        pass

    def destroy(self):
        if not self.is_destroyed:
            self._report_destroyed()
            self._destroyed()

    def _attached(self, attached_to):
        pass

    def _detached(self):
        pass

    def report_attachment(self, target: HasLifetime):
        self._attached_to = target
        self._attached(target)

    def report_detachment(self):
        self._attached_to = None
        if self.is_alive:
            self._detached()

    def attach_to(self, target: HasLifetime):
        target.attach_component(self)

    def __repr__(self):
        def attached_suffix():
            if self._attached_to is not None:
                return f" attached to {self._attached_to}"
            else:
                return ""
        return f"<Component {type(self).__name__}{attached_suffix()}>"


class System(HasLifetime):
    def __init__(self):
        super().__init__()

    def _started(self):
        pass

    def start(self):
        print(f"System {type(self).__name__} started")
        self._started()

    def _stopped(self):
        pass

    def stop(self):
        print(f"System {type(self).__name__} stopped")
        self._report_destroyed()
        self._stopped()

    def __repr__(self):
        return f"<System {type(self).__name__}>"
