from enum import Enum, auto
from typing import Tuple, Union, Callable, List, Optional, cast
import pygame
from pygame.sprite import DirtySprite

from kelvin452.engine.fonts import default_font
from kelvin452.engine.game import game
from kelvin452.engine.systems.base import System
from kelvin452.engine.systems.ticking import TickOrder
from kelvin452.engine.systems.world import Entity, EntityComponent, EntityCompatibleComponent


class RenderingGroup(Enum):
    DEFAULT = auto()
    UI = auto()


class RenderingSystem(System):
    """
    Le moteur de rendu.
    """

    def __init__(self):
        super().__init__()
        self._fps_sprite = FpsSprite()
        self._sprites = pygame.sprite.LayeredDirty()
        self._ui_sprites = pygame.sprite.LayeredUpdates(self._fps_sprite)
        self.group_map = {
            RenderingGroup.DEFAULT: self._sprites,
            RenderingGroup.UI: self._ui_sprites
        }
        self.__background: Optional[pygame.Surface] = None
        self.repaint_next_frames = 15
        self.queued_rendering_actions: List[Callable] = []
        "Le groupe de sprites qui met à jour que ce qui est nécessaire."

    def _started(self):
        surface = pygame.Surface((1280, 720))
        surface.fill((50, 0, 0))
        self.__background = surface

    def render(self, screen: pygame.Surface):
        """Effectue le rendu de tous les sprites à l'écran.

        Args:
            screen (pygame.Surface): L'écran où sont affichés les sprites
        """
        # Repeindre tout l'écran s'il y a de l'interface. LayeredUpdates est buggé
        # pour aucune raison.
        # if len(self._ui_sprites.sprites()) >= 1:
        #     self.repaint_next_frames = max(self.repaint_next_frames, 2)

        # Faire le rendu de l'écran entier en cas d'actions exceptionnelles
        # parce que le groupe principal doit être rerendu en entier s'il y a des
        # sprites retirés de l'interface.
        if len(self.queued_rendering_actions) > 0 or self.repaint_next_frames > 0 or \
                len(self._ui_sprites.lostsprites) > 0:
            self._sprites.set_clip()

        # Mettre à jour les FPS
        self._fps_sprite.update()

        # Remplir avec l'arrière plan
        self._sprites.clear(screen, self.__background)
        # Faire le rendu de tous les sprites
        updated_region = self._sprites.draw(screen) + self._ui_sprites.draw(screen)

        for action in self.queued_rendering_actions:
            action()
        self.queued_rendering_actions.clear()

        # Mettre à jour l'écran
        pygame.display.update(updated_region)  # type: ignore

        if self.repaint_next_frames > 0:
            self.repaint_next_frames -= 1

    def add_sprite(self, sprite: pygame.sprite.Sprite, group=None):
        """Ajoute un sprite qui sera affiché à l'écran.

        Args:
            sprite (pygame.sprite.Sprite): Le sprite à afficher
        """
        if group is None:
            group = sprite.group if isinstance(sprite, KelvinSprite) else RenderingGroup.DEFAULT

        self.group_map[group].add(sprite)

    def remove_sprite(self, sprite: pygame.sprite.Sprite, group=None):
        """Retirer un sprite de l'écran

        Args:
            sprite (pygame.sprite.Sprite): Le sprite à retirer
        """
        if group is None:
            group = sprite.group if isinstance(sprite, KelvinSprite) else RenderingGroup.DEFAULT

        self.group_map[group].remove(sprite)

    def queue_rendering_action(self, action: Callable):
        """
        Ajouter une fonction à exécuter lors du rendu. Cette fonction sera
        lancée uniquement sur la frame actuelle.
        :param action: La fonction à lancer
        """
        self.queued_rendering_actions.append(action)

    @property
    def background(self):
        return self.__background

    @background.setter
    def background(self, value):
        self.__background = value
        self.repaint_next_frames += 1


EMPTY_SURFACE = pygame.Surface((0, 0))


class KelvinSprite(EntityCompatibleComponent, DirtySprite):
    rect: pygame.Rect
    image: pygame.surface.Surface  # Bye bye optional

    def __init__(self, image: pygame.surface.Surface, location: Tuple[float, float] = (0, 0),
                 auto_update=True, layer=0, group=RenderingGroup.DEFAULT):
        super().__init__()
        self.image = image
        self.rect = image.get_rect().move(*location)
        self.layer = layer
        self.blendmode = pygame.BLEND_ALPHA_SDL2  # Blend mode pour plus de performance
        self.group = group
        self.__auto_update = auto_update
        self.__position = pygame.Vector2(self.rect.x, self.rect.y)
        self.dirty = 1
        game.ticking.add_tick_function(lambda: self._update_dirty_state(), TickOrder.PRE_RENDER).attach_to(self)

    @property
    def position(self):
        return self.__position

    @position.setter
    def position(self, value: Union[pygame.Vector2, Tuple[float, float]]):
        value = pygame.Vector2(value)
        if self.__position != value:
            self.__position = value
            self.dirty = 1

    def change_layer(self, layer):
        if len(self.groups()) == 0:
            self.layer = layer
        else:
            self.__get_group().change_layer(self, layer)

    def move_to_front(self):
        self.__get_group().move_to_front(self)

    def move_to_back(self):
        self.__get_group().move_to_back(self)

    def __get_group(self) -> pygame.sprite.LayeredDirty:
        return cast(pygame.sprite.LayeredDirty, self.groups()[0])

    def _entity_tick(self, entity: Entity):
        if self.__auto_update:
            self.position = entity.position

    def _attached(self, attached_to):
        game.renderer.add_sprite(self)

    def _destroyed(self):
        self.kill()

    def _update_dirty_state(self):
        if not self.dirty:
            if self.rect.x != self.position.x or self.rect.y != self.position.y:
                self.dirty = 1
        if self.dirty:
            self.rect.x, self.rect.y = self.position.xy


class FpsSprite(pygame.sprite.DirtySprite):
    empty = pygame.surface.Surface((0, 0))

    def __init__(self):
        super().__init__()
        self.image = FpsSprite.empty
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.had_log_fps_before = False

    def update(self, *args, **kwargs):
        if game.log_fps:
            text = f"{game.clock.get_fps():.0f} FPS"
            self.image = default_font.render(text, True, (255, 255, 255))
            self.dirty = 1
            self.had_log_fps_before = True
        else:
            self.image = FpsSprite.empty
            if self.had_log_fps_before:
                self.dirty = 1
                self.had_log_fps_before = False


make_sprite = KelvinSprite
