# ASTEROIDES v2.0
# Utilitários matemáticos e de desenho.

import math
from random import random, uniform
from typing import Iterable

import pygame as pg
import config as C

Vec = pg.math.Vector2


def wrap_pos(pos: Vec) -> Vec:
    return Vec(pos.x % C.WIDTH, pos.y % C.HEIGHT)


def angle_to_vec(deg: float) -> Vec:
    rad = math.radians(deg)
    return Vec(math.cos(rad), math.sin(rad))


def rand_unit_vec() -> Vec:
    a = uniform(0, math.tau)
    return Vec(math.cos(a), math.sin(a))


def rand_edge_pos() -> Vec:
    if random() < 0.5:
        x = uniform(0, C.WIDTH)
        y = 0 if random() < 0.5 else C.HEIGHT
    else:
        x = 0 if random() < 0.5 else C.WIDTH
        y = uniform(0, C.HEIGHT)
    return Vec(x, y)


def draw_poly(surface: pg.Surface, pts: Iterable, color=None):
    pg.draw.polygon(surface, color or C.WHITE, list(pts), width=1)


def draw_circle(surface: pg.Surface, pos: Vec, r: int, color=None):
    pg.draw.circle(surface, color or C.WHITE, pos, r, width=1)


def text(surface: pg.Surface, font, s: str, x: int, y: int, color=None):
    surf = font.render(s, True, color or C.WHITE)
    surface.blit(surf, surf.get_rect(topleft=(x, y)))


def text_center(surface: pg.Surface, font, s: str, cx: int, cy: int,
                color=None):
    surf = font.render(s, True, color or C.WHITE)
    surface.blit(surf, surf.get_rect(center=(cx, cy)))
