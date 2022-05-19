import pygame.key

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