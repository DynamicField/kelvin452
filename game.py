import pygame


class Game:
    def __init__(self):
        pygame.init()

    def start(self):
        pygame.display.set_caption("Kelvin 452")
        screen = pygame.display.set_mode((1280, 720))

        # define a variable to control the main loop
        running = True

        # main loop
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            screen.fill((220, 25, 42))
            pygame.display.flip()