from typing import Callable, Any
import pygame
import time
import kelvin452.systems as systems


class Game:
    def __init__(self):
        pygame.init()
        uninitialized: Any = None
        self.renderer: systems.RenderingSystem = uninitialized
        self.world: systems.WorldSystem = uninitialized
        self.on_start_funcs = []
        self.delta_time = 1 / 60  # assume some start time

    def initialize_game(self):
        self.renderer = systems.RenderingSystem()
        self.world = systems.WorldSystem()

    def on_start(self, func: Callable):
        self.on_start_funcs.append(func)

    def start(self):
        pygame.display.set_caption("Kelvin 452")
        screen = pygame.display.set_mode((1280, 720))

        for start_func in self.on_start_funcs:
            start_func()

        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.renderer.render(screen)
            self.world.tick()
            clock.tick(60)
            self.delta_time = clock.get_time() / 1000
            print(f"clock time: {clock.get_time() :.2f}ms ({clock.get_fps()} FPS)")

    @property
    def viewport(self):
        return pygame.display.get_window_size()


game = Game()
