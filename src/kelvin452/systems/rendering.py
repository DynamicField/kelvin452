from functools import cached_property
from typing import Tuple
import pygame


class RenderingSystem:
    """
    Le moteur de rendu.
    """
    def __init__(self):
        self._sprites = pygame.sprite.LayeredDirty()
        "Le groupe de sprites qui met à jour que ce qui est nécessaire."

    def render(self, screen: pygame.surface.Surface):
        """Effectue le rendu de tous les sprites à l'écran.

        Args:
            screen (pygame.surface.Surface): L'écran où sont affichés les sprites
        """
        # Remplir avec l'arrière plan
        self._sprites.clear(screen, self._background)
        # Faire le rendu de tous les sprites 
        updated_region = self._sprites.draw(screen)
        # Mettre à jour l'écran
        pygame.display.update(updated_region) # type: ignore

    @cached_property
    def _background(self):
        """L'arrière plan du jeu.

        Returns:
            pygame.surface.Surface: L'arrière-plan
        """
        surface = pygame.surface.Surface((1280, 720))
        surface.fill((50, 0, 0))
        return surface

    def add_sprite(self, sprite: pygame.sprite.Sprite):
        """Ajoute un sprite qui sera affiché à l'écran.

        Args:
            sprite (pygame.sprite.Sprite): Le sprite à afficher
        """
        self._sprites.add(sprite)

    def remove_sprite(self, sprite: pygame.sprite.Sprite):
        """Retirer un sprite de l'écran

        Args:
            sprite (pygame.sprite.Sprite): Le sprite à retirer
        """
        self._sprites.remove(sprite)


def make_sprite(image: pygame.surface.Surface, location: Tuple[float, float]) -> pygame.sprite.DirtySprite:
    """Crée un sprite (DirtySprite) avec l'image fournie à la position indiquée.

    Args:
        image (pygame.surface.Surface): L'image du sprite
        location (Tuple[float, float]): La position du sprite (x, y)

    Returns:
        pygame.sprite.DirtySprite: Le sprite créé
    """
    sprite = pygame.sprite.DirtySprite()
    sprite.image = image
    sprite.rect = image.get_rect().move(*location)
    return sprite
