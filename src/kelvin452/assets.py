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

    def sprite(self, path: str):
        path = "sprites/" + path
        if path not in self.assets:
            self.assets[path] = AssetLibrary.load_image(path)

        return self.assets[path]


all_assets = AssetLibrary()
