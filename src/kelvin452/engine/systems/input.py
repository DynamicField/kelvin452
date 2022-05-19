import pygame.key
from pygame import Vector2

from kelvin452.engine.systems import System


class InputSystem(System):
    def __init__(self):
        super().__init__()

    @staticmethod
    def is_key_down(key) -> bool:
        """
        Retourne True si la touche donnée est appuyée, ou False si elle est lâchée.
        Les touches du paramètre ``key`` correspondent aux valeurs de pygame,
        tel que ``pygame.K_<touche>``.

        :param key: La touche appuyée
        :return: True si la touche est appuyée, False sinon
        """
        return pygame.key.get_pressed()[key]

    @staticmethod
    def is_mouse_left_click_down() -> bool:
        return pygame.mouse.get_pressed()[0]

    @staticmethod
    def is_mouse_right_click_down() -> bool:
        return pygame.mouse.get_pressed()[1]

    @staticmethod
    def get_mouse_position() -> Vector2:
        return Vector2(pygame.mouse.get_pos())