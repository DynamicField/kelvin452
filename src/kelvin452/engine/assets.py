import os
import pygame
from functools import cached_property

assets_location = os.path.realpath(
    os.path.join(os.path.dirname(__file__), "../../../assets")
)

assets = {}


def load_image(relative_path: str):
    return pygame.image.load(os.path.join(assets_location, relative_path)).convert_alpha()


def sprite(path: str):
    path = "sprites/" + path
    if path not in assets:
        assets[path] = load_image(path)

    return assets[path]


def background(path: str):
    path = "background/" + path
    if path not in assets:
        assets[path] = load_image(path)

    return assets[path]
