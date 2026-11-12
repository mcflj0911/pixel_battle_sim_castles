"""Doodads: the props scattered over the battlefield (trees, rocks, bushes, wrecks, camps). They are only scenery:
they do not change the battle. Each is drawn once from shapes into a small outlined sprite, and placed with a seeded
random generator so the field looks the same every run. Campfires and lanterns glow at night."""
import math
import random

import pygame

from scenery import KINDS, place  # noqa: F401  (the renderer imports these from here)
from sprites import INK, outlined, shade

GLOWING = ("campfire", "lantern")


def _g(white, c):
    return (255, 255, 255) if white else c


def build(kind, variant=0, white=False):
    """The sprite for one kind of doodad (outlined). `variant` (0-2) changes colours and shapes a little."""
    rnd = random.Random(variant * 977 + len(kind))
    leaf = [(54, 104, 52), (70, 112, 48), (44, 92, 70)][variant % 3]
    if kind == "oak":
        s = pygame.Surface((22, 26), pygame.SRCALPHA)
        pygame.draw.rect(s, (84, 58, 36), (9, 14, 4, 12))
        pygame.draw.rect(s, (58, 40, 26), (9, 14, 1, 12))
        for cx, cy, r in ((11, 8, 8), (5, 11, 5), (17, 11, 5), (11, 4, 5)):
            pygame.draw.circle(s, shade(leaf, 0.7), (cx, cy), r)
        for cx, cy, r in ((10, 7, 6), (5, 10, 3), (16, 10, 3)):
            pygame.draw.circle(s, leaf, (cx, cy), r)
        pygame.draw.circle(s, shade(leaf, 1.35), (8, 5), 3)
        return outlined(s)
    if kind == "pine":
        s = pygame.Surface((14, 28), pygame.SRCALPHA)
        pygame.draw.rect(s, (74, 52, 32), (6, 22, 2, 6))
        dark = (30, 70, 52) if variant != 1 else (36, 78, 44)
        for i, (w, y) in enumerate(((13, 10), (11, 6), (8, 2))):
            top = y + 2 if i else 1
            pygame.draw.polygon(s, dark, [(7, top), (7 - w // 2, y + 10), (7 + w // 2, y + 10)])
            pygame.draw.polygon(s, shade(dark, 1.4), [(7, top), (7 - w // 2, y + 10), (7, y + 10)])
        return outlined(s)
    if kind == "deadtree":
        s = pygame.Surface((16, 22), pygame.SRCALPHA)
        wood = (92, 76, 62)
        pygame.draw.line(s, wood, (8, 22), (8, 6), 2)
        pygame.draw.line(s, wood, (8, 14), (2, 7), 1)
        pygame.draw.line(s, wood, (8, 10), (14, 3), 1)
        pygame.draw.line(s, wood, (8, 17), (13, 12), 1)
        pygame.draw.line(s, shade(wood, 1.3), (7, 6), (7, 20))
        return outlined(s)
    if kind == "bush":
        s = pygame.Surface((12, 8), pygame.SRCALPHA)
        for cx, cy, r in ((4, 5, 3), (8, 5, 3), (6, 3, 3)):
            pygame.draw.circle(s, shade(leaf, 0.75), (cx, cy), r)
        pygame.draw.circle(s, leaf, (6, 3), 2)
        if variant == 2:                                        # a berry bush
            for p in ((3, 4), (8, 5), (6, 2)):
                s.set_at(p, (190, 40, 50))
        return outlined(s)
    if kind in ("rock", "boulder"):
        big = kind == "boulder"
        w, h = (14, 10) if big else (7, 5)
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        base = [(118, 116, 112), (104, 102, 100), (126, 118, 104)][variant % 3]
        pygame.draw.polygon(s, base, [(0, h - 1), (1, h // 2), (w // 3, 0), (w - 2, 1), (w - 1, h - 1)])
        pygame.draw.polygon(s, shade(base, 1.3), [(1, h // 2), (w // 3, 0), (w // 2, 1), (w // 3, h // 2)])
        pygame.draw.line(s, shade(base, 0.7), (1, h - 1), (w - 1, h - 1))
        return outlined(s)
    if kind == "flowers":
        s = pygame.Surface((9, 6), pygame.SRCALPHA)
        for x in range(1, 9, 2):
            pygame.draw.line(s, (50, 96, 44), (x, 5), (x, 3))
        col = [(240, 220, 90), (236, 236, 240), (200, 110, 200)][variant % 3]
        for x, y in ((1, 2), (3, 1), (5, 2), (7, 1)):
            s.set_at((x, y), col)
        return s
    if kind == "grass":
        s = pygame.Surface((8, 6), pygame.SRCALPHA)
        for x, h in ((1, 3), (3, 5), (5, 4), (7, 3)):
            pygame.draw.line(s, shade((70, 120, 54), 0.8 + 0.2 * (x % 2)), (x, 5), (x + (x % 3) - 1, 5 - h))
        return s
    if kind == "stump":
        s = pygame.Surface((8, 6), pygame.SRCALPHA)
        pygame.draw.rect(s, (92, 64, 40), (1, 2, 6, 4))
        pygame.draw.ellipse(s, (170, 134, 90), (1, 0, 6, 3))
        return outlined(s)
    if kind == "log":
        s = pygame.Surface((14, 6), pygame.SRCALPHA)
        pygame.draw.rect(s, (96, 66, 42), (0, 1, 14, 5))
        pygame.draw.rect(s, (130, 96, 62), (0, 1, 14, 1))
        pygame.draw.ellipse(s, (176, 140, 94), (11, 0, 3, 6))
        return outlined(s)
    if kind == "fence":
        s = pygame.Surface((18, 9), pygame.SRCALPHA)
        for x in (1, 8, 15):
            pygame.draw.rect(s, (110, 78, 48), (x, 1, 2, 8))
        for y in (3, 6):
            pygame.draw.rect(s, (140, 104, 66), (0, y, 18, 1))
        return outlined(s)
    if kind == "barrel":
        s = pygame.Surface((7, 9), pygame.SRCALPHA)
        pygame.draw.rect(s, (116, 80, 46), (0, 1, 7, 8))
        pygame.draw.rect(s, (60, 60, 66), (0, 3, 7, 1))
        pygame.draw.rect(s, (60, 60, 66), (0, 7, 7, 1))
        pygame.draw.rect(s, (150, 112, 70), (1, 0, 5, 2))
        return outlined(s)
    if kind == "crates":
        s = pygame.Surface((13, 11), pygame.SRCALPHA)
        for x, y, w in ((0, 5, 6), (6, 5, 6), (3, 0, 6)):
            pygame.draw.rect(s, (138, 100, 58), (x, y, w, 6))
            pygame.draw.rect(s, (92, 64, 38), (x, y, w, 6), 1)
            pygame.draw.line(s, (92, 64, 38), (x, y), (x + w - 1, y + 5))
        return outlined(s)
    if kind == "hay":
        s = pygame.Surface((12, 9), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (206, 176, 82), (0, 0, 12, 9))
        pygame.draw.ellipse(s, (232, 206, 110), (2, 1, 6, 4))
        pygame.draw.line(s, (150, 118, 50), (1, 5), (10, 5))
        return outlined(s)
    if kind == "wagon":
        s = pygame.Surface((22, 14), pygame.SRCALPHA)
        pygame.draw.rect(s, (112, 78, 46), (2, 4, 18, 5))
        pygame.draw.rect(s, (150, 112, 70), (2, 4, 18, 1))
        pygame.draw.polygon(s, (214, 204, 180), [(4, 4), (8, 0), (16, 0), (20, 4)])      # a canvas hood
        for cx in (5, 17):
            pygame.draw.circle(s, (60, 42, 26), (cx, 10), 3)
            pygame.draw.circle(s, (130, 94, 56), (cx, 10), 1)
        pygame.draw.line(s, (96, 66, 40), (20, 8), (26 if False else 21, 12))
        return outlined(s)
    if kind == "spear":
        s = pygame.Surface((7, 16), pygame.SRCALPHA)
        pygame.draw.line(s, (150, 110, 64), (3, 15), (4, 3))
        pygame.draw.polygon(s, (206, 210, 222), [(4, 0), (6, 4), (2, 4)])
        pygame.draw.polygon(s, [(190, 50, 50), (60, 90, 190), (200, 200, 60)][variant % 3], [(4, 5), (7, 6), (4, 9)])
        return outlined(s)
    if kind == "shield":
        s = pygame.Surface((9, 9), pygame.SRCALPHA)
        col = [(190, 50, 50), (60, 90, 190), (80, 80, 84)][variant % 3]
        pygame.draw.circle(s, col, (4, 4), 4)
        pygame.draw.circle(s, shade(col, 1.4), (4, 4), 2)
        pygame.draw.line(s, (60, 40, 26), (1, 1), (7, 7))                  # cracked across
        return outlined(s)
    if kind == "bones":
        s = pygame.Surface((10, 6), pygame.SRCALPHA)
        pygame.draw.circle(s, (226, 220, 200), (3, 3), 2)
        s.set_at((2, 3), INK)
        s.set_at((4, 3), INK)
        pygame.draw.line(s, (226, 220, 200), (5, 4), (9, 2))
        pygame.draw.line(s, (226, 220, 200), (5, 2), (9, 5))
        return outlined(s)
    if kind == "arrows":
        s = pygame.Surface((10, 10), pygame.SRCALPHA)
        for x, lean in ((2, -1), (5, 0), (8, 1)):
            pygame.draw.line(s, (130, 96, 56), (x, 9), (x + lean, 2))
            s.set_at((x + lean, 1), (220, 220, 226))
            s.set_at((x, 8), (190, 60, 60))
        return s
    if kind == "tent":
        s = pygame.Surface((20, 14), pygame.SRCALPHA)
        col = [(206, 196, 170), (170, 80, 70), (80, 100, 170)][variant % 3]
        pygame.draw.polygon(s, col, [(10, 0), (0, 13), (19, 13)])
        pygame.draw.polygon(s, shade(col, 0.7), [(10, 0), (10, 13), (19, 13)])
        pygame.draw.polygon(s, (36, 28, 24), [(10, 6), (7, 13), (13, 13)])
        pygame.draw.line(s, (110, 80, 50), (10, 0), (10, -1 if False else 0))
        return outlined(s)
    if kind == "campfire":
        s = pygame.Surface((12, 11), pygame.SRCALPHA)
        for a in (0.4, 1.4, 2.4):
            pygame.draw.line(s, (96, 64, 38), (6, 9), (6 + int(math.cos(a) * 5), 9 - int(abs(math.sin(a)) * 2)), 2)
        pygame.draw.polygon(s, (240, 120, 30), [(6, 1), (3, 8), (9, 8)])
        pygame.draw.polygon(s, (255, 214, 90), [(6, 4), (4, 8), (8, 8)])
        return outlined(s)
    if kind == "lantern":
        s = pygame.Surface((7, 18), pygame.SRCALPHA)
        pygame.draw.rect(s, (70, 52, 36), (3, 4, 1, 14))
        pygame.draw.rect(s, (70, 52, 36), (1, 3, 5, 1))
        pygame.draw.rect(s, (255, 214, 100), (2, 4, 3, 4))
        pygame.draw.rect(s, (60, 60, 66), (2, 4, 3, 4), 1)
        return outlined(s)
    raise ValueError(kind)
