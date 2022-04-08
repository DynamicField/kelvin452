import os
import pygame
from functools import cached_property

assets_location = os.path.realpath(
    os.path.join(os.path.dirname(__file__), "../../assets")
)


class AssetLibrary:
    def __init__(self):
        self.assets = {}

    @staticmethod
    def load_image(relative_path: str):
        return pygame.image.load(os.path.join(assets_location, relative_path)).convert_alpha()

    @cached_property
    def fire_sprite(self) -> pygame.Surface:
        return AssetLibrary.load_image("sprites/fire.png")


all_assets = AssetLibrary()
