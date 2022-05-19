from typing import Callable, Any, Dict, Type, TypeVar
import pygame
import kelvin452.engine.systems as systems
from kelvin452.engine.systems.base import System
from kelvin452.engine.systems.ticking import TickOrder


class Game:
    """
    Représente l'état du jeu et gère les systèmes du jeu.
    """

    def __init__(self):
        pygame.init()
        uninitialized: Any = None  # Pour que les types arrêtent de se plaindre
        self.renderer: systems.RenderingSystem = uninitialized
        "Le système de rendu, qui gère les sprites à mettre sur l'écran."
        self.world: systems.WorldSystem = uninitialized
        "Le système du monde, qui gère les entités présentes à l'écran."
        self.ticking: systems.TickingSystem = uninitialized
        "Le système des ticks qui gère les fonctions appelées à chaque frame."
        self.event: systems.EventSystem = uninitialized
        "Le système d'event qui gère les évènements du jeu."
        self.input: systems.InputSystem = uninitialized
        "Le système d'input qui gère la souris et le clavier"
        self.__systems: Dict[type, System] = {}
        self.__game_started = False
        self.on_start_funcs = []
        self.delta_time = 1 / 60  # assume some start time
        "Le temps (en secondes) passé entre la frame précédente et la frame actuelle."

    def initialize_game(self):
        """
        Initialise les systèmes du jeu.
        """
        self.renderer = self.add_system(systems.RenderingSystem())
        self.world = self.add_system(systems.WorldSystem())
        self.ticking = self.add_system(systems.TickingSystem())
        self.event = self.add_system(systems.EventSystem())
        self.input = self.add_system(systems.InputSystem())

    def on_start(self, func: Callable):
        """Ajoute une fonction à lancer lorsque le jeu commence.

        Args:
            func (Callable): La fonction à lancer
        """
        self.on_start_funcs.append(func)

    def start(self):
        """
        Lance le jeu avec la boucle initiale de pygame.
        Appelle les fonctions on_start. 
        """
        pygame.display.set_caption("Kelvin 452")
        # Fênetre 1280x720
        screen = pygame.display.set_mode((1280, 720))

        self.__game_started = True
        for system in self.__systems.values():
            system.start()
        for start_func in self.on_start_funcs:
            start_func()

        # Boucle du jeu
        clock = pygame.time.Clock()
        while True:
            self.event.process_events()
            if not self.event.continue_running:
                break

            self.ticking.run_ticks(TickOrder.ENTITY)  # Lancer le tick des entités
            self.renderer.render(screen)  # Faire le rendu des sprites.
            self.ticking.run_ticks(TickOrder.POST_RENDER)  # Lancer le tick après le rendu

            # On utilise une horloge avec un max de 60 fps
            clock.tick(60)
            self.delta_time = clock.get_time() / 1000  # Secondes écoulées

            # Écrire les FPS dans la console
            print(f"clock time: {clock.get_time() :.2f}ms ({clock.get_fps()} FPS)")

        for system in self.__systems.values():
            system.stop()

    S = TypeVar('S', bound='System')

    def get_system(self, system_type: Type[S]) -> S:
        assert system_type in systems, f"Cannot find system of type {system_type}."
        return self.__systems[system_type]

    def add_system(self, system: S) -> S:
        self.__systems[type(system)] = system
        if self.__game_started:
            system.start()
        return system

    @property
    def viewport(self):
        """Retourne un vecteur 2D avec les dimensions de la fenêtre.

        Returns:
            (int, int): Les dimensions de la fenêtre en pixels, largeur x hauteur
        """
        return pygame.math.Vector2(pygame.display.get_window_size())


game = Game()
