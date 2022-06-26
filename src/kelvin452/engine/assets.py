import os
import pygame
import sys


def is_packaged():
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')


assets_location = os.path.realpath(
    os.path.join(os.path.dirname(__file__), "../../assets" if is_packaged() else "../../../assets")
)

assets = {}


def load_image(relative_path: str):
    return pygame.image.load(os.path.join(assets_location, relative_path)).convert_alpha()


def load(folder: str, path: str):
    path = os.path.join(folder, path)
    if path not in assets:
        assets[path] = load_image(path)

    return assets[path]


def sprite(path: str) -> pygame.Surface:
    return load("sprites", path)


def grounds(path: str) -> pygame.Surface:
    return load("grounds", path)


def ui(path: str) -> pygame.Surface:
    return load("ui", path)
