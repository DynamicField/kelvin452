from typing import Tuple, Union, Callable, List
import pygame
from pygame.sprite import DirtySprite

from kelvin452.engine.game import game
from kelvin452.engine.systems.base import System
from kelvin452.engine.systems.world import Entity, EntityComponent


class RenderingSystem(System):
    """
    Le moteur de rendu.
    """

    def __init__(self):
        super().__init__()
        self._sprites = pygame.sprite.LayeredDirty()
        self.background: pygame.Surface
        self.queued_rendering_actions: List[Callable] = []
        self.last_frame_custom_render = False
        "Le groupe de sprites qui met à jour que ce qui est nécessaire."

    def _started(self):
        surface = pygame.Surface((1280, 720))
        surface.fill((50, 0, 0))
        self.background = surface

    def render(self, screen: pygame.Surface):
        """Effectue le rendu de tous les sprites à l'écran.

        Args:
            screen (pygame.Surface): L'écran où sont affichés les sprites
        """
        # Faire le rendu de l'écran entier en cas d'actions exceptionnelles
        if len(self.queued_rendering_actions) > 0:
            self._sprites.set_clip()

        # Remplir avec l'arrière plan
        self._sprites.clear(screen, self.background)
        # Faire le rendu de tous les sprites 
        updated_region = self._sprites.draw(screen)

        for action in self.queued_rendering_actions:
            action()
        self.queued_rendering_actions.clear()

        # Mettre à jour l'écran
        pygame.display.update(updated_region)  # type: ignore

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

    def queue_rendering_action(self, action: Callable):
        self.queued_rendering_actions.append(action)


class KelvinSprite(EntityComponent, DirtySprite):
    rect: pygame.Rect
    image: pygame.surface.Surface  # Bye bye optional

    def __init__(self, image: pygame.surface.Surface, location: Tuple[float, float] = (0, 0),
                 auto_update=True):
        super().__init__()
        self.image = image
        self.rect = image.get_rect().move(*location)
        self.__auto_update = auto_update

    @property
    def position(self):
        return pygame.Vector2(self.rect.x, self.rect.y)

    @position.setter
    def position(self, value: Union[pygame.Vector2, Tuple[float, float]]):
        value = pygame.Vector2(value)
        if self.position != value:
            self.rect.x, self.rect.y = value.xy
            self.dirty = 1

    def _entity_tick(self, entity: Entity):
        if self.__auto_update:
            self.position = entity.position

    def _attached(self, attached_to):
        game.renderer.add_sprite(self)

    def _destroyed(self):
        self.kill()


make_sprite = KelvinSprite
