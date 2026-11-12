"""Unit art for Pixel BS. Each unit is drawn from a small piece of character art: every character is a colour
(see palette()). Foot soldiers, archers and riders have two walk frames; each sprite gets a dark outline so it reads
against grass and stone. The sprites face right; the renderer flips them for units facing left."""
import math

import pygame

GOLD = (236, 196, 84)
INK = (22, 16, 14)
SKIN = (226, 188, 148)


def shade(color, k):
    return tuple(max(0, min(255, int(c * k))) for c in color)


def palette(color, white=False, variant=0, hero=False):
    """Character -> colour. B/b/l are the side's colour (base, dark, light); p is the helmet plume."""
    plume = GOLD if hero else (shade(color, 1.35), (236, 232, 222), shade(color, 0.55))[variant % 3]
    pal = {
        "B": color, "b": shade(color, 0.58), "l": shade(color, 1.3), "p": plume,
        "h": (128, 132, 146), "H": (206, 210, 222), "M": (74, 76, 90),
        "s": SKIN, "S": shade(SKIN, 0.78), "e": INK,
        "k": (92, 64, 40), "K": (54, 38, 26), "w": (150, 110, 64), "W": (196, 156, 100),
        "g": GOLD, "c": (214, 206, 186), "r": (122, 82, 50), "R": (84, 56, 34), "q": (160, 112, 70),
        "f": (255, 150, 40), "F": (255, 226, 120), "x": (170, 36, 36),
    }
    if white:
        return {k: (255, 255, 255) for k in pal}
    return pal


def from_art(rows, pal):
    h, w = len(rows), max(len(r) for r in rows)
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in pal:
                s.set_at((x, y), pal[ch])
    return s


def outlined(s, col=INK):
    """A copy of the sprite with a one-pixel outline all round it."""
    w, h = s.get_size()
    out = pygame.Surface((w + 2, h + 2), pygame.SRCALPHA)
    m = pygame.mask.from_surface(s).to_surface(setcolor=col, unsetcolor=(0, 0, 0, 0))
    for dx, dy in ((0, 1), (2, 1), (1, 0), (1, 2)):
        out.blit(m, (dx, dy))
    out.blit(s, (1, 1))
    return out


# ---------------------------------------------------------------------------------------------- foot soldier
# 9 wide. The shield is on the left, the spear on the right.
FOOT_TOP = [
    ".......H.",
    "..ppp..w.",
    "..hHhh.w.",
    "..hsse.w.",
    "..MsM..w.",
    ".lllhBsw.",
    "lbbbBBBw.",
    "lbgbBBBw.",
    "lbbbBBB..",
    ".lbb.kB..",
]
FOOT_LEGS = (
    ["..mm.mm..", "..KK.KK.."],                       # standing
    ["..mm..mm.", ".KK...KK."],                       # mid stride
)

# ---------------------------------------------------------------------------------------------- archer
ARCHER_TOP = [
    "...KKK.w.",
    "..KkkkKww",
    "..kssek.w",
    "..kMsM..w",
    "cKBBBBcww",
    "KKBBBBssw",
    "kKBBBB.ww",
    ".kBlBB..w",
    "..bBBb.w.",
    "..kkkk...",
]
ARCHER_LEGS = (
    ["..kk.kk..", "..KK.KK.."],
    ["..kk..kk.", ".KK...KK."],
)

# ---------------------------------------------------------------------------------------------- rider
RIDER_UP = [
    ".ppp.",
    "hHhhh",
    "hsse.",
    ".MsM.",
    "hBBBb",
    "lBBBb",
]


def _compose(top, legs, frame):
    return top + legs[frame % 2]


def foot(color, archer=False, hero=False, white=False, frame=0, wounded=False, routing=False, variant=0):
    pal = palette(color, white, variant, hero)
    rows = _compose(ARCHER_TOP if archer else FOOT_TOP, ARCHER_LEGS if archer else FOOT_LEGS, frame)
    s = from_art(rows, pal)
    if wounded:
        for x in (2, 3, 4):
            s.set_at((x, 2), pal["c"])
        s.set_at((3, 2), pal["x"])
    if routing:
        s.set_at((1, 2), pal["s"])
        s.set_at((1, 3), pal["s"])
        s.set_at((0, 1), pal["s"])
    if hero and not archer:
        for y in range(5, 10):
            s.set_at((1, y), pal["g"])
    return outlined(s)


def rider(color, hero=False, white=False, frame=0, variant=0):
    """A mounted knight: a horse drawn from shapes (barded in the side's colours) with a rider and a couched lance."""
    return outlined(_rider_raw(color, hero, white, frame, variant))


def _rider_raw(color, hero=False, white=False, frame=0, variant=0, horse_col=(128, 88, 54)):
    pal = palette(color, white, variant, hero)
    W = (255, 255, 255)
    horse = W if white else horse_col
    dark = W if white else shade(horse, 0.6)
    hi = W if white else shade(horse, 1.25)
    s = pygame.Surface((19, 16), pygame.SRCALPHA)
    for lx, hind in ((4, 1), (6, 1), (12, 0), (14, 0)):               # four legs, striding alternately
        off = (-1 if hind else 1) * (frame % 2)
        pygame.draw.rect(s, dark, (lx + off, 11, 2, 5))
    pygame.draw.line(s, dark, (3, 7), (0, 11), 2)                     # tail
    pygame.draw.ellipse(s, horse, (3, 6, 13, 6))                      # body
    pygame.draw.line(s, hi, (6, 7), (13, 7))
    pygame.draw.polygon(s, horse, [(13, 8), (15, 2), (18, 4), (16, 9)])    # neck
    pygame.draw.line(s, dark, (14, 2), (13, 8), 2)                    # mane
    pygame.draw.polygon(s, horse, [(15, 2), (18, 3), (18, 6), (16, 6)])    # head
    pygame.draw.rect(s, dark, (17, 5, 2, 2))                          # muzzle
    s.set_at((15, 1), dark)                                           # ear
    s.set_at((16, 3), INK)                                            # eye
    pygame.draw.rect(s, pal["B"], (5, 8, 8, 3))                       # the horse's barding
    pygame.draw.rect(s, pal["l"], (5, 8, 8, 1))
    pygame.draw.rect(s, pal["g"] if not white else W, (5, 10, 8, 1))  # a gold hem
    pygame.draw.line(s, pal["w"], (11, 5), (18, 1))                   # the couched lance
    s.set_at((18, 1), pal["H"])
    s.blit(from_art(RIDER_UP, pal), (6, 0))
    if hero:
        pygame.draw.rect(s, pal["g"], (5, 11, 8, 1))
    return s


# ---------------------------------------------------------------------------------------------- the heroes
# Four kinds, each drawn from shapes and in two styles: 0 for Ravensmere (plumes, gold, white), 1 for Ironvale
# (horns, black iron, red). They are bigger than the rank and file, so a hero stands out in a crowd.
def _w(white, col):
    return (255, 255, 255) if white else col


def champion(color, style=0, white=False, frame=0):
    """A heavy knight with a great kite shield and a sword (style 0) or a horned helm and a two-headed axe (style 1)."""
    pal = palette(color, white, 0, True)
    steel = _w(white, (176, 182, 196) if style == 0 else (96, 98, 108))
    dark = _w(white, (86, 90, 104) if style == 0 else (46, 46, 54))
    hi = _w(white, (226, 230, 240) if style == 0 else (150, 152, 164))
    s = pygame.Surface((16, 17), pygame.SRCALPHA)
    step = frame % 2
    pygame.draw.rect(s, dark, (5 - step, 12, 2, 5))                      # legs
    pygame.draw.rect(s, dark, (8 + step, 12, 2, 5 - step))
    pygame.draw.rect(s, steel, (5, 6, 6, 7))                              # breastplate
    pygame.draw.rect(s, pal["B"], (6, 8, 4, 5))                           # tabard in the side's colour
    pygame.draw.rect(s, pal["g"], (5, 11, 6, 1))                          # belt
    pygame.draw.rect(s, hi, (4, 5, 3, 3))                                 # pauldrons
    pygame.draw.rect(s, hi, (10, 5, 3, 3))
    pygame.draw.rect(s, steel, (6, 2, 5, 5))                              # great helm
    pygame.draw.rect(s, hi, (7, 2, 3, 1))
    pygame.draw.rect(s, _w(white, (22, 16, 14)), (7, 4, 4, 1))            # visor slit
    if style == 0:
        pygame.draw.line(s, pal["p"], (8, 2), (7, 0))                      # a gold plume
        pygame.draw.line(s, pal["p"], (8, 2), (10, 0))
        pygame.draw.line(s, pal["p"], (9, 2), (11, 1))
    else:
        for hx, hy, dx in ((6, 2, -1), (10, 2, 1)):                         # horns
            pygame.draw.line(s, _w(white, (222, 214, 190)), (hx, hy), (hx + dx * 2, hy - 2))
            s.set_at((hx + dx * 2, hy - 3), _w(white, (222, 214, 190)))
    shield = [(0, 6), (5, 6), (5, 12), (3, 16), (0, 12)]
    pygame.draw.polygon(s, pal["B"], shield)                               # the shield
    pygame.draw.polygon(s, pal["g"], shield, 1)
    pygame.draw.line(s, pal["l"], (2, 7), (2, 13))
    s.set_at((2, 9), pal["g"])
    pygame.draw.rect(s, _w(white, SKIN), (12, 8, 2, 2))                    # the weapon hand
    if style == 0:
        pygame.draw.line(s, _w(white, (232, 236, 246)), (13, 8), (13, 0))   # a long blade
        pygame.draw.rect(s, pal["g"], (12, 8, 3, 1))
        s.set_at((13, 0), (255, 255, 255))
    else:
        pygame.draw.line(s, _w(white, (110, 78, 46)), (13, 15), (13, 1))    # axe haft
        pygame.draw.polygon(s, steel, [(13, 1), (10, 0), (10, 5), (13, 4)])
        pygame.draw.polygon(s, steel, [(13, 1), (15, 0), (15, 5), (13, 4)])
        pygame.draw.line(s, hi, (10, 1), (10, 4))
    return outlined(s)


def commander(color, style=0, white=False, frame=0):
    """A mounted commander: a caparisoned charger, a streaming cloak, a plumed helm and a banner on the lance."""
    pal = palette(color, white, 0, True)
    horse = (236, 232, 222) if style == 0 else (44, 40, 46)
    raw = _rider_raw(color, True, white, frame, 0, horse_col=horse)
    s = pygame.Surface((23, 24), pygame.SRCALPHA)
    cloak = _w(white, pal["b"])
    sway = frame % 2
    pygame.draw.polygon(s, cloak, [(9, 14), (3, 18 + sway), (5, 22), (10, 20)])           # the cloak, behind
    s.blit(raw, (3, 8))
    pygame.draw.line(s, _w(white, (150, 110, 64)), (19, 14), (19, 1))                    # the banner pole
    pygame.draw.polygon(s, pal["B"], [(19, 1), (22, 2 + sway), (22, 6 + sway), (19, 6)])
    pygame.draw.line(s, pal["g"], (19, 1), (22, 2 + sway))
    pygame.draw.line(s, pal["g"], (19, 6), (22, 6 + sway))
    pygame.draw.line(s, pal["p"], (10, 9), (9, 6))                                       # a tall plume
    pygame.draw.line(s, pal["p"], (9, 9), (7, 7))
    return outlined(s)


def ranger(color, style=0, white=False, frame=0):
    """A hooded archer with a long bow and a quiver. Style 1 carries a bow wrapped in flame."""
    pal = palette(color, white, 0, True)
    cloak = _w(white, pal["b"] if style == 0 else shade(color, 0.75))
    cloak_hi = _w(white, pal["B"])
    s = pygame.Surface((15, 17), pygame.SRCALPHA)
    step = frame % 2
    pygame.draw.rect(s, _w(white, (60, 44, 30)), (4 - step, 13, 2, 4))       # boots
    pygame.draw.rect(s, _w(white, (60, 44, 30)), (7 + step, 13, 2, 4 - step))
    pygame.draw.polygon(s, cloak, [(5, 5), (10, 5), (11, 14), (3, 14)])      # the cloak
    pygame.draw.polygon(s, cloak_hi, [(6, 6), (9, 6), (9, 13), (6, 13)])
    pygame.draw.rect(s, _w(white, pal["g"]), (5, 10, 5, 1))                  # belt
    pygame.draw.polygon(s, cloak, [(5, 5), (7, 0), (10, 5)])                 # the hood
    pygame.draw.rect(s, _w(white, SKIN), (6, 3, 3, 3))                       # face
    s.set_at((8, 4), _w(white, INK))
    pygame.draw.line(s, _w(white, (110, 78, 46)), (4, 5), (3, 12), 2)       # the quiver on the back
    for qx in (3, 4):
        s.set_at((qx, 3), _w(white, (226, 226, 226)))
    bow = _w(white, (150, 110, 64))
    pygame.draw.arc(s, bow, pygame.Rect(8, 0, 6, 17), -1.45, 1.45, 1)        # the long bow
    pygame.draw.line(s, _w(white, (230, 226, 210)), (12, 1), (12, 16))      # its string
    pygame.draw.line(s, _w(white, (120, 88, 48)), (9, 8), (13, 8))           # an arrow nocked
    s.set_at((13, 8), (255, 255, 255))
    if style == 1:                                                           # flame licking the bow tips
        for fy, up in ((1, -1), (15, 1)):
            s.set_at((13, fy), _w(white, (255, 150, 40)))
            s.set_at((13, fy + up), _w(white, (255, 226, 120)))
    return outlined(s)


def mage(color, style=0, white=False, frame=0):
    """A robed caster with a staff topped by a glowing orb: golden (style 0, a healer) or violet (style 1, a witch)."""
    pal = palette(color, white, 0, True)
    robe = _w(white, pal["B"] if style == 0 else shade(color, 0.7))
    trim = _w(white, pal["g"])
    glow = (255, 232, 130) if style == 0 else (190, 110, 255)
    glow2 = (255, 255, 220) if style == 0 else (232, 190, 255)
    s = pygame.Surface((15, 18), pygame.SRCALPHA)
    sway = frame % 2
    pygame.draw.polygon(s, robe, [(5, 6), (9, 6), (11 + sway, 17), (3 - sway, 17)])     # the robe flares to the hem
    pygame.draw.line(s, trim, (3 - sway, 17), (11 + sway, 17))
    pygame.draw.line(s, trim, (7, 7), (7, 16))                                           # a gold stripe
    pygame.draw.rect(s, _w(white, (236, 232, 222) if style == 0 else shade(color, 0.5)), (4, 6, 6, 2))   # mantle
    pygame.draw.rect(s, _w(white, SKIN), (6, 3, 3, 3))                                   # face
    s.set_at((8, 4), _w(white, INK))
    if style == 0:                                                                       # a mitre
        pygame.draw.polygon(s, _w(white, (240, 236, 224)), [(5, 3), (7, 0), (10, 3)])
        pygame.draw.line(s, trim, (5, 3), (10, 3))
    else:                                                                                # a pointed hat with a brim
        pygame.draw.polygon(s, robe, [(5, 3), (8, 0), (10, 3)])
        pygame.draw.line(s, trim, (4, 3), (11, 3))
    pygame.draw.line(s, _w(white, (130, 92, 56)), (12, 17), (12, 4))                    # the staff
    pygame.draw.circle(s, _w(white, glow), (12, 3), 2)
    s.set_at((12, 3), _w(white, glow2))
    pygame.draw.rect(s, _w(white, SKIN), (10, 9, 2, 2))
    return outlined(s)


def king(color, style=0, white=False, frame=0):
    """A king in a gold crown, ermine-trimmed cloak and mail, holding a sceptre. Style 1 is a tyrant in black and red."""
    pal = palette(color, white, 0, True)
    cloak = _w(white, pal["B"] if style == 0 else shade(color, 0.6))
    ermine = _w(white, (240, 236, 228))
    s = pygame.Surface((15, 19), pygame.SRCALPHA)
    sway = frame % 2
    pygame.draw.rect(s, _w(white, (60, 44, 30)), (5, 15, 2, 4))
    pygame.draw.rect(s, _w(white, (60, 44, 30)), (8, 15, 2, 4))
    pygame.draw.polygon(s, cloak, [(4, 6), (11, 6), (13 + sway, 17), (2 - sway, 17)])     # the cloak
    pygame.draw.rect(s, ermine, (4, 6, 8, 2))                                              # ermine collar
    for ex in (3 - sway, 7, 11 + sway):
        s.set_at((ex, 16), _w(white, INK))
    pygame.draw.rect(s, ermine, (2 - sway, 17, 12 + 2 * sway, 1))
    pygame.draw.rect(s, _w(white, (150, 156, 170)), (6, 8, 4, 7))                          # mail
    pygame.draw.rect(s, pal["g"], (6, 12, 4, 1))
    pygame.draw.rect(s, _w(white, SKIN), (6, 3, 4, 4))                                     # face
    s.set_at((9, 4), _w(white, INK))
    pygame.draw.rect(s, pal["g"], (5, 1, 6, 2))                                            # the crown
    for cx in (5, 7, 9):
        s.set_at((cx, 0), pal["g"])
    s.set_at((8, 2), _w(white, (220, 40, 50)))
    if frame >= 2:                                                                         # cheering: sceptre thrust high
        pygame.draw.rect(s, _w(white, SKIN), (12, 6, 2, 3))
        pygame.draw.line(s, _w(white, (214, 186, 90)), (13, 8), (13, 1))
        pygame.draw.circle(s, pal["g"], (13, 1), 1)
        pygame.draw.rect(s, _w(white, SKIN), (2, 6, 2, 3))                                 # the other arm up too
    else:
        pygame.draw.line(s, _w(white, (214, 186, 90)), (13, 17), (13, 4))                  # the sceptre
        pygame.draw.circle(s, pal["g"], (13, 3), 2)
        s.set_at((13, 3), _w(white, (220, 40, 50)))
        pygame.draw.rect(s, _w(white, SKIN), (11, 9, 2, 2))
    return outlined(s)


EXTRA_KINDS = ("longbow", "halberdier", "berserker", "pavise_cross", "war_dog", "mangonel", "ram_crew", "griffon",
               "harpy", "longship", "galley", "catapult_ship", "landing_boat", "siege_tower")
HEROES = {"champion": champion, "commander": commander, "ranger": ranger, "mage": mage, "king": king}


# ---------------------------------------------------------------------------------------------- flyers
# Both have three wing poses (0 raised, 1 level, 2 beaten down); the renderer cycles 0, 1, 2, 1.
def _wing_y(frame):
    return (1, 6, 11)[frame % 3]


def wyvern(color, white=False, frame=0):
    """A wyvern: a long green-grey body, a barbed tail, bat wings with membranes in the side's colour, and a rider
    with a plumed helm. It drops pots of burning pitch."""
    pal = palette(color, white, 0, True)
    body = _w(white, (92, 112, 78))
    belly = _w(white, (170, 168, 120))
    dark = _w(white, (52, 66, 46))
    mem = _w(white, shade(color, 0.85))
    ty = _wing_y(frame)
    s = pygame.Surface((26, 18), pygame.SRCALPHA)
    pygame.draw.polygon(s, dark, [(9, 8), (4, ty), (14, ty + 1), (15, 8)])                 # the far wing, behind
    pygame.draw.polygon(s, body, [(3, 9), (9, 7), (17, 7), (21, 9), (24, 11), (21, 13), (15, 14), (8, 13)])   # body
    pygame.draw.polygon(s, belly, [(9, 12), (17, 12), (20, 13), (14, 14), (9, 13)])
    pygame.draw.polygon(s, body, [(3, 9), (0, 12), (1, 15), (4, 12)])                      # the tail ...
    pygame.draw.polygon(s, dark, [(0, 15), (3, 14), (2, 17)])                              # ... and its barb
    pygame.draw.polygon(s, body, [(21, 8), (25, 8), (25, 11), (22, 11)])                   # the head
    pygame.draw.rect(s, dark, (25, 9, 1, 2))
    s.set_at((23, 9), _w(white, (255, 210, 60)))                                           # a yellow eye
    pygame.draw.polygon(s, mem, [(11, 8), (2, ty), (9, ty + (2 if ty < 8 else -2)), (15, ty + 3), (22, ty + 1), (17, 8)])   # the near wing
    pygame.draw.line(s, dark, (11, 8), (2, ty))
    pygame.draw.line(s, dark, (14, 8), (22, ty + 1))
    pygame.draw.line(s, dark, (13, 8), (15, ty + 3))
    for lx in (10, 16):                                                                    # talons
        pygame.draw.line(s, dark, (lx, 13), (lx, 16))
    pygame.draw.rect(s, _w(white, shade(color, 0.7)), (13, 3, 4, 5))                       # the rider
    pygame.draw.rect(s, _w(white, (176, 182, 196)), (13, 0, 4, 3))
    pygame.draw.line(s, pal["p"], (14, 0), (13, -0))
    s.set_at((15, 0), pal["p"])
    pygame.draw.line(s, _w(white, (150, 110, 64)), (17, 5), (22, 3))                       # a short lance
    return outlined(s)


def hawk(color, white=False, frame=0):
    """A giant hawk: brown wings and body, a white head, a yellow beak and a rider with a lance. It hunts flyers."""
    pal = palette(color, white, 0, True)
    brown = _w(white, (124, 88, 56))
    dark = _w(white, (78, 54, 34))
    cream = _w(white, (240, 234, 220))
    ty = _wing_y(frame)
    s = pygame.Surface((24, 17), pygame.SRCALPHA)
    pygame.draw.polygon(s, dark, [(10, 8), (6, ty), (15, ty + 1), (14, 8)])               # the far wing
    pygame.draw.ellipse(s, brown, (4, 7, 15, 6))                                           # the body
    pygame.draw.polygon(s, dark, [(4, 9), (0, 10), (0, 13), (5, 12)])                      # the tail feathers
    pygame.draw.polygon(s, cream, [(17, 6), (21, 6), (22, 10), (18, 10)])                  # the white head
    pygame.draw.polygon(s, _w(white, (255, 200, 40)), [(21, 8), (24, 9), (21, 10)])        # the beak
    s.set_at((20, 7), _w(white, INK))
    pygame.draw.polygon(s, brown, [(11, 8), (5, ty), (18, ty + 2), (16, 8)])              # the near wing
    for fx in range(6, 18, 3):                                                             # feather tips
        pygame.draw.line(s, dark, (11, 8), (fx, ty + (1 if fx > 11 else 0)))
    pygame.draw.polygon(s, pal["B"], [(5, ty), (9, ty), (8, ty - 1 if ty > 3 else ty + 1)])   # side-coloured wing tips
    pygame.draw.line(s, dark, (11, 12), (11, 15))                                          # talons
    pygame.draw.rect(s, pal["B"], (10, 2, 4, 5))                                           # the rider
    pygame.draw.rect(s, _w(white, (176, 182, 196)), (10, 0, 4, 3))
    s.set_at((11, -0), pal["p"])
    pygame.draw.line(s, _w(white, (150, 110, 64)), (13, 4), (21, 1))                       # a long lance
    s.set_at((21, 1), _w(white, (236, 240, 248)))
    return outlined(s)


def ballista(color, white=False, pose=0):
    """A ballista on a wheeled carriage, its stock tilted up at the sky. pose 0 has the bowstring drawn with a bolt
    laid on it; poses 3 to 5 show the arms sprung forward and the bolt gone; poses 1 and 2 are the string released."""
    s = pygame.Surface((22, 16), pygame.SRCALPHA)
    wood = (255, 255, 255) if white else (140, 98, 52)
    dark = (255, 255, 255) if white else (78, 52, 30)
    light = (255, 255, 255) if white else (186, 140, 84)
    iron = (255, 255, 255) if white else (150, 154, 164)
    pygame.draw.rect(s, wood, (1, 12, 18, 2))
    pygame.draw.rect(s, light, (1, 12, 18, 1))
    for cx in (5, 15):
        pygame.draw.circle(s, dark, (cx, 14), 3)
        pygame.draw.circle(s, wood, (cx, 14), 1)
    pygame.draw.rect(s, wood, (9, 8, 3, 5))                            # the upright
    pygame.draw.line(s, wood, (3, 11), (16, 5), 2)                     # the stock, tilted up toward the sky
    pygame.draw.line(s, light, (3, 10), (16, 4))
    drawn = pose <= 0 or pose >= 5                                     # string back (ready) or still winding
    held = pose <= 2
    ax, ay = (15, 3) if not drawn else (13, 4)                          # the bow arms
    pygame.draw.line(s, dark, (16, 5), (ax + 1, ay - 3), 2)
    pygame.draw.line(s, dark, (16, 5), (ax + 3, ay + 7), 2)
    sx = 11 if drawn else 17                                            # the bowstring
    pygame.draw.line(s, (255, 255, 255) if white else (226, 222, 204), (ax + 1, ay - 3), (sx, 6))
    pygame.draw.line(s, (255, 255, 255) if white else (226, 222, 204), (sx, 6), (ax + 3, ay + 7))
    if held:                                                            # the bolt, laid ready
        pygame.draw.line(s, wood if not white else (255, 255, 255), (sx, 6), (21, 1))
        s.set_at((21, 1), iron)
        s.set_at((20, 1), iron)
    pygame.draw.polygon(s, color if not white else (255, 255, 255), [(7, 6), (10, 7), (7, 10)])
    return outlined(s)


#@@NEWUNITS@@
# ============================================================= new foot units (hand-drawn like the rank and file)
EXTRA = {"G": (74, 112, 60), "d": (44, 72, 40), "y": (212, 176, 92), "z": (150, 56, 38), "t": (196, 78, 52),
         "o": (232, 140, 40), "n": (110, 104, 100), "j": (66, 60, 58)}


def _pal(color, white=False, variant=0, hero=False):
    pal = palette(color, white, variant, hero)
    for k, v in EXTRA.items():
        pal[k] = (255, 255, 255) if white else v
    return pal


def _blank(w, h):
    return pygame.Surface((w, h), pygame.SRCALPHA)


def _put(s, pal, pts, ch):
    """Sets the pixels `pts` (a list of (x, y)) to the palette colour `ch`."""
    for x, y in pts:
        if 0 <= x < s.get_width() and 0 <= y < s.get_height():
            s.set_at((x, y), pal[ch])


# ---------------------------------------------------------------------------------------------- longbowman
LONGBOW_TOP = [
    "...GGG....",
    "..GdddG...",
    "..GsseG...",
    "..dsMs....",
    ".kdBBBd...",
    ".dBBBBss..",
    ".kBBBB....",
    ".kBlBB....",
    "..bBBb....",
    "..kkkk....",
]
LONGBOW_LEGS = (["..kk.kk...", "..KK.KK..."], ["..kk..kk..", ".KK...KK.."])


def longbow(color, white=False, frame=0):
    """A longbowman in a green hood: a bow as tall as he is, a quiver at his hip, and a long, steady draw."""
    pal = _pal(color, white)
    s = from_art(LONGBOW_TOP + LONGBOW_LEGS[frame % 2], pal)
    stave = [8, 9, 10, 10, 10, 10, 10, 10, 10, 10, 9, 8]
    for y, x in enumerate(stave):                                  # the stave, tall as the man
        s.set_at((x, y), pal["w"] if y % 3 else pal["W"])
    pull = 6 if frame % 2 else 8                                   # the string, drawn back a little on the stride
    for y in range(1, 11):
        x = 8 if y in (1, 10) else pull if abs(y - 5) < 3 else 8
        s.set_at((x, y), pal["c"])
    s.set_at((8, 5), pal["s"])
    s.set_at((pull, 5), pal["s"])
    _put(s, pal, [(7, 5), (6, 5)], "c") if frame % 2 == 0 else None  # an arrow nocked on the string
    for y in (3, 4, 5):                                            # the quiver: fletching over the shoulder
        s.set_at((1, y - 3), pal["W"]) if y == 3 else None
    s.set_at((1, 3), pal["c"])
    s.set_at((0, 4), pal["w"])
    s.set_at((0, 5), pal["w"])
    return outlined(s)


# ---------------------------------------------------------------------------------------------- halberdier
HALB_TOP = [
    "........H.",
    "........H.",
    "..ppp...wH",
    "..hHhh.hwH",
    "..hsse..wH",
    "..MsM...w.",
    ".hhhBhhsw.",
    ".hBBBBhsw.",
    ".hBgBBh.w.",
    "..bBBb..w.",
]
HALB_LEGS = (["..hh.hh.w.", "..KK.KK.w."], ["..hh..hh.w", ".KK...KK.w"])


def halberdier(color, white=False, frame=0):
    """A footman in mail with a halberd: a spike, an axe-blade and a hook on a long pole, held in two hands. It
    skewers cavalry."""
    pal = _pal(color, white)
    s = from_art(HALB_TOP + HALB_LEGS[frame % 2], pal)
    if frame % 2:                                                   # the pole tips with his stride
        s.set_at((9, 10), pal["w"])
    return outlined(s)


# ---------------------------------------------------------------------------------------------- berserker
BERS_TOP = [
    "...x.x.x.HH",
    "...xxxxx.wH",
    "...xsese.w.",
    "...xxsxx.w.",
    ".s.sBsBs.w.",
    "HsssBsBss.w"[:11],
    "Hw.sssss.w.",
    ".w.kkkkk...",
    "...kRkRk...",
]
BERS_LEGS = (["...ss.ss...", "...kk.kk..."], ["...ss..ss..", "..kk...kk.."])


def berserker(color, white=False, frame=0):
    """A berserker: bare to the waist, painted in the side's colour, wild red hair and beard, an axe in each hand. No
    armour, no fear, and the more he is hurt the harder he swings."""
    pal = _pal(color, white)
    s = from_art(BERS_TOP + BERS_LEGS[frame % 2], pal)
    s.set_at((0, 4), pal["w"]) if False else None
    return outlined(s)


# ---------------------------------------------------------------------------------------------- pavise crossbowman
PAV_TOP = [
    ".hhh.....w",
    "hHHHHh...w",
    ".hsse.kkkw",
    ".MsMs.ccc.",
    ".bBBBhhhhh",
    ".bBBBhWBwh",
    ".bBlBhWBwh",
    "..bBBhWBwh",
    "..bBBhWBwh",
]
PAV_LEGS = (["..kk.hWBwh", "..KK.hWBwh", "....hhhhh."], [".kk..hWBwh", ".KK..hWBwh", "....hhhhh."])


def pavise_cross(color, white=False, frame=0):
    """A crossbowman behind his pavise, a tall shield stood on the ground and painted with the side's stripe. The bolt
    from his heavy crossbow punches through a shield wall."""
    pal = _pal(color, white)
    return outlined(from_art(PAV_TOP + PAV_LEGS[frame % 2], pal))


# ---------------------------------------------------------------------------------------------- war dog
DOG_A = [
    ".........R.R.",
    ".........rrrR",
    "R......rrrrrse",
    "Rr.qqqqqqrrccx",
    ".rqqqqqqqBqc..",
    "..qqqqqqqqq...",
    "..r.r...q.q...",
    "..R.R...R.R...",
]
DOG_B = [
    ".........R.R.",
    ".........rrrR",
    ".R.....rrrrrse",
    "Rr.qqqqqqrrccx",
    ".rqqqqqqqBqc..",
    "..qqqqqqqqq...",
    "...rr....qq...",
    "..R..R..R..R..",
]


def war_dog(color, white=False, frame=0):
    """A war hound in a collar of the side's colour: lean and low, ears pricked, jaws open for a runner's heels."""
    pal = _pal(color, white)
    return outlined(from_art(DOG_A if frame % 2 == 0 else DOG_B, pal))


# ---------------------------------------------------------------------------------------------- mangonel
def mangonel(color, white=False, pose=0):
    """A mangonel: a squat frame with a skein of twisted rope across it, a long arm that ends in a cup, and a barrel
    of pitch beside it. pose 0 has the arm drawn back with a lit pot in the cup; poses 1 to 5 fling it up and over."""
    pal = _pal(color, white)
    W_ = lambda c: (255, 255, 255) if white else c
    wood, dark, light = W_((140, 98, 52)), W_((78, 52, 30)), W_((186, 140, 84))
    rope, band = W_((214, 196, 150)), W_((150, 128, 92))
    s = pygame.Surface((24, 18), pygame.SRCALPHA)
    pygame.draw.rect(s, wood, (1, 12, 22, 2))                               # the base
    pygame.draw.rect(s, light, (1, 12, 22, 1))
    for cx in (5, 18):                                                      # two big spoked wheels
        pygame.draw.circle(s, dark, (cx, 14), 3)
        pygame.draw.circle(s, wood, (cx, 14), 2)
        pygame.draw.line(s, dark, (cx - 2, 14), (cx + 2, 14))
        pygame.draw.line(s, dark, (cx, 12), (cx, 16))
    pygame.draw.rect(s, wood, (9, 6, 2, 6))                                 # the two uprights ...
    pygame.draw.rect(s, wood, (13, 6, 2, 6))
    pygame.draw.rect(s, rope, (9, 5, 6, 3))                                 # ... and the rope skein between them
    for bx in (10, 12, 14):
        pygame.draw.line(s, band, (bx, 5), (bx, 7))
    px, py = 12, 6
    ang = math.radians(CATAPULT_ARM[max(0, min(5, pose))])
    tx, ty = round(px + 10 * math.cos(ang)), round(py + 10 * math.sin(ang))
    pygame.draw.line(s, dark, (px, py), (tx, ty), 2)                        # the long arm
    pygame.draw.rect(s, dark, (tx - 1, ty - 1, 3, 3))                       # the cup
    if pose <= 2:                                                           # the pot of pitch, lit
        pygame.draw.rect(s, W_((52, 46, 44)), (tx - 1, ty - 3, 3, 2))
        s.set_at((tx, ty - 4), pal["o"])
        s.set_at((tx + 1, ty - 5), pal["F"])
        s.set_at((tx, ty - 5), pal["f"])
    pygame.draw.rect(s, W_((92, 66, 40)), (19, 8, 4, 5))                    # a barrel of pitch ...
    pygame.draw.rect(s, W_((52, 46, 44)), (19, 8, 4, 1))
    pygame.draw.line(s, W_((128, 132, 146)), (19, 10), (22, 10))
    s.set_at((20, 7), pal["o"])                                             # ... smouldering
    pygame.draw.polygon(s, pal["B"], [(3, 6), (8, 7), (3, 9)])              # the side's pennant
    pygame.draw.line(s, dark, (3, 5), (3, 11))
    return outlined(s)


# ---------------------------------------------------------------------------------------------- battering ram
def ram_crew(color, white=False, frame=0):
    """A battering ram under a roofed shed on wheels: a hide-covered roof with the side's stripe, the crew's legs
    showing below it, and a log with an iron head that swings back and forth as they push."""
    pal = _pal(color, white)
    W_ = lambda c: (255, 255, 255) if white else c
    wood, dark, light = W_((126, 88, 46)), W_((70, 46, 26)), W_((184, 138, 82))
    hide, hide2 = W_((120, 96, 70)), W_((96, 76, 54))
    iron, ironl = W_((128, 132, 146)), W_((206, 210, 222))
    s = pygame.Surface((34, 18), pygame.SRCALPHA)
    sw = 2 if frame % 2 else 0                                             # the log swings
    pygame.draw.rect(s, dark, (7 + sw, 11, 21, 2))                         # the ram's log, hung beneath the roof
    pygame.draw.rect(s, wood, (7 + sw, 11, 21, 1))
    pygame.draw.rect(s, iron, (27 + sw, 10, 4, 4))                         # the iron head
    pygame.draw.rect(s, ironl, (27 + sw, 10, 4, 1))
    pygame.draw.polygon(s, iron, [(31 + sw, 10), (31 + sw, 13), (33 + sw, 12)])
    for bx in (12, 18, 24):                                                # the crew, seen under the roof's edge
        bob = 1 if (bx // 6 + frame) % 2 else 0
        pygame.draw.rect(s, pal["s"], (bx, 9 + bob, 2, 2))                  # head
        pygame.draw.rect(s, pal["h"], (bx - 1, 11 + bob, 4, 3))             # mail
        pygame.draw.rect(s, pal["K"], (bx, 14, 1, 2 - bob))                 # legs
        pygame.draw.rect(s, pal["K"], (bx + 2, 14, 1, 2 - bob))
    pygame.draw.polygon(s, hide2, [(3, 9), (6, 3), (26, 3), (29, 9)])       # the roof: hides on a frame
    pygame.draw.polygon(s, hide, [(4, 8), (7, 4), (25, 4), (27, 8)])
    for rx in range(8, 26, 5):                                             # ribs
        pygame.draw.line(s, hide2, (rx, 4), (rx - 1, 8))
    pygame.draw.line(s, light, (6, 3), (26, 3))
    pygame.draw.rect(s, pal["B"], (3, 8, 26, 2))                           # the side's stripe along the eaves
    pygame.draw.rect(s, pal["l"], (3, 8, 26, 1))
    pygame.draw.rect(s, dark, (3, 10, 1, 5))                               # the posts
    pygame.draw.rect(s, dark, (28, 10, 1, 5))
    for cx in (7, 24):                                                     # the wheels
        pygame.draw.circle(s, dark, (cx, 15), 2)
        s.set_at((cx, 15), wood)
    pygame.draw.line(s, pal["k"], (16, 0), (16, 3))                        # a banner pole on the ridge
    pygame.draw.polygon(s, pal["B"], [(16, 0), (21, 1), (16, 3)])
    return outlined(s)


# ---------------------------------------------------------------------------------------------- griffon rider
def griffon(color, white=False, frame=0):
    """A griffon: a lion's body and tail, an eagle's head, wings and talons, with a plumed rider and a pennant."""
    pal = _pal(color, white, 0, True)
    tan, tan2, dark = _w(white, (196, 150, 78)), _w(white, (150, 106, 52)), _w(white, (104, 70, 36))
    cream, gold = _w(white, (244, 238, 222)), _w(white, (255, 200, 40))
    ty = _wing_y(frame)
    s = pygame.Surface((31, 20), pygame.SRCALPHA)
    pygame.draw.polygon(s, dark, [(13, 8), (6, ty - (1 if ty > 3 else 0)), (19, ty + 1), (18, 8)])      # the far wing
    pygame.draw.line(s, tan2, (7, 15), (3, 12), 2)                                            # the lion's tail ...
    pygame.draw.polygon(s, dark, [(0, 11), (3, 10), (4, 14), (1, 14)])                        # ... with its tuft
    pygame.draw.ellipse(s, tan, (4, 8, 17, 7))                                                # the body
    pygame.draw.line(s, tan2, (6, 14), (19, 14))                                              # the belly shadow
    for lx in (8, 11):                                                                        # lion hind legs, paws down
        pygame.draw.rect(s, tan2, (lx, 14, 2, 3))
        pygame.draw.rect(s, tan, (lx, 17, 3, 1))
    pygame.draw.polygon(s, cream, [(18, 7), (24, 6), (25, 11), (19, 13)])                     # the white eagle chest
    pygame.draw.polygon(s, cream, [(22, 4), (27, 5), (27, 9), (23, 9)])                       # ... and head
    pygame.draw.polygon(s, gold, [(27, 6), (30, 8), (27, 9)])                                 # the hooked beak
    s.set_at((25, 6), INK)                                                                    # the eye
    pygame.draw.line(s, tan2, (22, 4), (20, 3))                                               # head crest
    for lx in (19, 22):                                                                       # eagle talons
        pygame.draw.line(s, gold, (lx, 14), (lx + 1, 17))
        s.set_at((lx + 2, 17), gold)
    wing = [(12, 8), (3, ty + 1), (8, ty - (1 if ty > 3 else -1)), (13, ty + 1), (18, ty), (22, ty + 3), (19, 8)]
    pygame.draw.polygon(s, tan, wing)                                                          # the near wing, broad
    pygame.draw.polygon(s, pal["B"], [(12, 8), (3, ty + 1), (8, ty + (2 if ty < 6 else 0)), (13, 8)])   # side-coloured coverts
    for fx in (4, 8, 13, 18, 22):                                                              # feather fingers
        pygame.draw.line(s, dark, (12, 8), (fx, ty + (1 if fx < 8 else 3 if fx > 20 else 2)))
    pygame.draw.rect(s, pal["B"], (11, 2, 4, 6))                                              # the rider
    pygame.draw.rect(s, _w(white, (176, 182, 196)), (11, 0, 4, 3))
    s.set_at((12, 0), pal["p"])
    s.set_at((13, 0), pal["p"])
    pygame.draw.line(s, _w(white, (150, 110, 64)), (15, 4), (22, 1))                          # his lance
    s.set_at((22, 1), _w(white, (236, 240, 248)))
    pygame.draw.polygon(s, pal["l"], [(10, 3), (5, 2), (10, 6)])                              # a trailing pennant
    return outlined(s)


# ---------------------------------------------------------------------------------------------- harpy
def harpy(color, white=False, frame=0):
    """A harpy: a woman's body and wild hair, great feathered wings, a bird's feathered thighs and hooked talons, and
    clawed hands reaching forward. She rakes the men below as she passes."""
    pal = _pal(color, white)
    feather, feather2 = _w(white, (118, 96, 84)), _w(white, (76, 58, 52))
    hair = _w(white, (44, 34, 34))
    ty = _wing_y(frame)
    s = pygame.Surface((22, 22), pygame.SRCALPHA)
    pygame.draw.polygon(s, feather2, [(11, 9), (5, ty), (8, ty + 6), (15, ty + 4), (14, 9)])             # the far wing
    wing = [(10, 9), (0, ty), (1, ty + 4), (5, ty + 7), (10, ty + 7), (13, ty + 4)]
    pygame.draw.polygon(s, feather, wing)                                                          # the near wing, broad
    for fx, fy in ((0, ty), (1, ty + 4), (5, ty + 7), (10, ty + 7)):                               # feather fingers
        pygame.draw.line(s, feather2, (10, 9), (fx, fy))
    pygame.draw.polygon(s, pal["B"], [(0, ty), (3, ty + 1), (1, ty + 4)])                          # side-coloured primaries
    pygame.draw.polygon(s, feather2, [(4, 12), (0, 15), (3, 16), (7, 14)])                    # tail feathers
    pygame.draw.polygon(s, feather, [(7, 12), (14, 11), (15, 15), (9, 16)])                   # feathered thighs
    for lx in (10, 13):                                                                       # bird legs and talons
        pygame.draw.line(s, pal["y"], (lx, 15), (lx + 1, 18))
        pygame.draw.line(s, pal["y"], (lx + 1, 18), (lx + 3, 19))
        pygame.draw.line(s, pal["y"], (lx + 1, 18), (lx - 1, 19))
    pygame.draw.polygon(s, pal["s"], [(9, 5), (13, 5), (14, 12), (9, 12)])                    # the torso
    pygame.draw.polygon(s, pal["B"], [(9, 8), (14, 8), (14, 12), (9, 12)])                    # a bodice in the side's colour
    pygame.draw.line(s, pal["l"], (9, 8), (14, 8))
    pygame.draw.rect(s, pal["s"], (10, 2, 4, 4))                                              # the head
    pygame.draw.polygon(s, hair, [(9, 1), (14, 1), (15, 4), (13, 3), (9, 3), (7, 7), (9, 7)])  # wild flowing hair
    pygame.draw.line(s, hair, (9, 4), (7, 8))
    s.set_at((13, 3), INK)
    s.set_at((13, 4), pal["x"])                                                               # a snarling mouth
    pygame.draw.line(s, pal["s"], (13, 8), (18, 9))                                           # the reaching arm
    pygame.draw.line(s, pal["c"], (18, 9), (20, 8))                                           # claws
    pygame.draw.line(s, pal["c"], (18, 9), (20, 10))
    return outlined(s)


# ============================================================= ships (they sail the water lane, facing right)
def _hull(s, white, pts, y_planks, deep=False):
    """A wooden hull: dark planks, a lighter stroke on each plank seam."""
    wood, dark, light = _w(white, (128, 90, 50)), _w(white, (84, 58, 34)), _w(white, (176, 132, 78))
    pygame.draw.polygon(s, dark if deep else wood, pts)
    for y in y_planks:
        xs = [p[0] for p in pts if abs(p[1] - y) < 8]
        pygame.draw.line(s, dark, (min(p[0] for p in pts) + (y - pts[0][1]) // 2 + 3, y),
                         (max(p[0] for p in pts) - (y - pts[0][1]) // 2 - 3, y))
    return wood, dark, light


def _oars(s, white, xs, y0, frame, n=2):
    """Oars dipping into the water: they swing with the frame."""
    oar = _w(white, (170, 130, 76))
    for i, x in enumerate(xs):
        k = (frame + i) % 3
        pygame.draw.line(s, oar, (x, y0), (x - 2 + k, y0 + 5))
        s.set_at((x - 2 + k, y0 + 5), _w(white, (214, 178, 112)))


def longship(color, white=False, frame=0):
    """A longship: a long low hull with a dragon prow, a row of round shields along the rail, oars, and a square sail
    striped in the side's colour. It rams other ships."""
    pal = _pal(color, white)
    wood, dark, light = _w(white, (128, 90, 50)), _w(white, (84, 58, 34)), _w(white, (176, 132, 78))
    s = pygame.Surface((44, 30), pygame.SRCALPHA)
    sway = (0, 1, 0)[frame % 3]
    # the sail first (it is behind the rail)
    pygame.draw.line(s, dark, (22, 3), (22, 17), 2)                                        # the mast
    pygame.draw.line(s, dark, (13, 4), (31, 4), 2)                                         # the yard
    sail = [(14, 5), (30, 5), (31 + sway, 12), (22, 14 + sway), (13 - sway, 12)]
    pygame.draw.polygon(s, pal["B"], sail)
    for y in (7, 9, 11, 13):                                                               # cream stripes
        pygame.draw.line(s, pal["c"], (14 - (y > 9), y), (30 + (y > 9), y)) if y in (7, 11) else None
    pygame.draw.line(s, pal["l"], (14, 5), (30, 5))
    pygame.draw.line(s, pal["b"], (22, 5), (22, 14))
    pygame.draw.polygon(s, pal["B"], [(22, 0), (27, 1), (22, 3)])                          # a masthead pennant
    # the hull, with a dragon prow and a curled stern
    hull = [(4, 15), (9, 17), (34, 17), (40, 13), (38, 22), (31, 25), (12, 25), (6, 21)]
    pygame.draw.polygon(s, wood, hull)
    for y in (19, 22):
        pygame.draw.line(s, dark, (8 + (y - 19), y), (36 - (y - 19), y))
    pygame.draw.line(s, light, (9, 17), (34, 17))
    pygame.draw.line(s, pal["B"], (7, 16), (37, 16))                                       # the rail in the side's colour
    for sx in range(9, 36, 4):                                                             # round shields along the rail
        pygame.draw.circle(s, pal["y"] if (sx // 4) % 2 else pal["B"], (sx, 18), 2)
        s.set_at((sx, 18), pal["h"])
    for hx in (11, 16, 27, 32):                                                            # crewmen's helmets above the rail
        pygame.draw.rect(s, pal["h"], (hx, 13, 3, 2))
        s.set_at((hx + 1, 14), pal["s"])
    pygame.draw.polygon(s, dark, [(4, 15), (2, 12), (3, 9), (6, 9), (5, 11), (6, 15)])      # the stern's curl
    pygame.draw.polygon(s, wood, [(36, 15), (40, 11), (41, 8), (43, 7), (44, 9), (42, 11), (41, 14), (38, 18)])   # the dragon neck
    pygame.draw.rect(s, dark, (42, 8, 2, 2))                                               # its head ...
    s.set_at((42, 8), pal["c"])                                                            # ... a tooth
    s.set_at((41, 8), pal["x"])                                                            # ... and a red eye
    pygame.draw.line(s, pal["B"], (22, 14), (22, 17))
    _oars(s, white, (13, 19, 25, 31), 21, frame)
    return outlined(s)


def galley(color, white=False, frame=0):
    """A galley: a broad deck with a raised stern castle and a forecastle, a banner, archers behind the rail, and two
    banks of oars. It shoots at ships and at men on the beach."""
    pal = _pal(color, white)
    wood, dark, light = _w(white, (128, 90, 50)), _w(white, (84, 58, 34)), _w(white, (176, 132, 78))
    stone = _w(white, (150, 152, 160))
    s = pygame.Surface((50, 34), pygame.SRCALPHA)
    pygame.draw.line(s, dark, (24, 4), (24, 20), 2)                                         # the mast and a furled sail
    pygame.draw.rect(s, pal["c"], (15, 8, 20, 3))
    pygame.draw.rect(s, pal["b"], (15, 10, 20, 1))
    pygame.draw.polygon(s, pal["B"], [(24, 0), (31, 2), (24, 4)])                           # the masthead pennant
    hull = [(3, 19), (46, 19), (44, 26), (38, 29), (10, 29), (5, 25)]
    pygame.draw.polygon(s, wood, hull)
    for y in (23, 26):
        pygame.draw.line(s, dark, (7 + (y - 23), y), (42 - (y - 23), y))
    pygame.draw.line(s, light, (3, 19), (46, 19))
    pygame.draw.rect(s, pal["B"], (4, 20, 42, 2))                                           # a broad stripe in the side's colour
    pygame.draw.rect(s, pal["l"], (4, 20, 42, 1))
    pygame.draw.rect(s, dark, (2, 10, 11, 10))                                              # the stern castle
    pygame.draw.rect(s, wood, (3, 11, 9, 8))
    for cx in (2, 6, 10):
        pygame.draw.rect(s, dark, (cx, 8, 3, 3))                                            # merlons
    pygame.draw.line(s, dark, (4, 3), (4, 8))                                               # a banner at the stern
    pygame.draw.polygon(s, pal["B"], [(4, 2), (10, 3), (4, 6)])
    pygame.draw.rect(s, dark, (38, 12, 9, 7))                                               # the forecastle
    pygame.draw.rect(s, wood, (39, 13, 7, 5))
    for cx in (38, 41, 44):
        pygame.draw.rect(s, dark, (cx, 10, 2, 3))
    for ax in (16, 22, 28, 34):                                                             # archers behind the rail
        pygame.draw.rect(s, pal["h"], (ax, 14, 3, 2))
        pygame.draw.rect(s, pal["s"], (ax, 16, 3, 1))
        pygame.draw.rect(s, pal["B"], (ax, 17, 3, 2))
        pygame.draw.line(s, pal["w"], (ax + 4, 12), (ax + 4, 18))                           # a longbow each
    for sx in range(14, 38, 4):                                                             # shields on the rail
        pygame.draw.circle(s, pal["y"] if (sx // 4) % 2 else pal["B"], (sx, 24), 1)
    _oars(s, white, (11, 17, 23, 29, 35), 26, frame)
    return outlined(s)


def catapult_ship(color, white=False, pose=0):
    """A catapult ship: a heavy, broad barge with a catapult bolted on its deck and a heap of stones. It throws at
    ships and at the beach. pose is the catapult's throwing pose, as for the catapult."""
    pal = _pal(color, white)
    wood, dark, light = _w(white, (128, 90, 50)), _w(white, (84, 58, 34)), _w(white, (176, 132, 78))
    iron = _w(white, (128, 132, 146))
    s = pygame.Surface((46, 34), pygame.SRCALPHA)
    hull = [(2, 20), (44, 20), (42, 27), (36, 30), (9, 30), (4, 26)]
    pygame.draw.polygon(s, wood, hull)
    for y in (24, 27):
        pygame.draw.line(s, dark, (6 + (y - 24), y), (40 - (y - 24), y))
    pygame.draw.line(s, light, (2, 20), (44, 20))
    pygame.draw.rect(s, pal["B"], (3, 21, 40, 2))
    pygame.draw.rect(s, pal["l"], (3, 21, 40, 1))
    for bx in (9, 21, 33):                                                                   # iron bands round the hull
        pygame.draw.rect(s, iron, (bx, 22, 2, 7))
    # the catapult
    pygame.draw.rect(s, dark, (9, 16, 22, 4))
    pygame.draw.rect(s, wood, (9, 16, 22, 1))
    pygame.draw.rect(s, dark, (18, 8, 3, 9))                                                 # the upright
    pygame.draw.rect(s, dark, (24, 8, 3, 9))
    ang = math.radians(CATAPULT_ARM[max(0, min(5, pose))])
    px, py = 21, 9
    tx, ty = round(px + 11 * math.cos(ang)), round(py + 11 * math.sin(ang))
    pygame.draw.line(s, dark, (px, py), (tx, ty), 2)
    pygame.draw.rect(s, dark, (tx - 2, ty - 1, 4, 3))
    if pose <= 2:
        pygame.draw.circle(s, _w(white, (150, 150, 156)), (tx, ty - 1), 2)
    for cx, cy in ((34, 17), (37, 17), (35, 14), (39, 17)):                                  # a heap of stones
        pygame.draw.circle(s, _w(white, (150, 150, 156)), (cx, cy), 2)
        s.set_at((cx - 1, cy - 1), _w(white, (190, 190, 196)))
    pygame.draw.line(s, dark, (6, 5), (6, 16))                                               # a stern post and pennant
    pygame.draw.polygon(s, pal["B"], [(6, 4), (13, 5), (6, 8)])
    for hx in (12, 28):                                                                      # the crew
        pygame.draw.rect(s, pal["h"], (hx, 13, 3, 2))
        pygame.draw.rect(s, pal["B"], (hx, 15, 3, 2))
    return outlined(s)


def landing_boat(color, white=False, frame=0):
    """A landing boat: a small open boat packed with soldiers, their shields along the rail. It rows to the beach and
    puts them ashore."""
    pal = _pal(color, white)
    wood, dark, light = _w(white, (128, 90, 50)), _w(white, (84, 58, 34)), _w(white, (176, 132, 78))
    s = pygame.Surface((34, 22), pygame.SRCALPHA)
    hull = [(2, 11), (6, 14), (28, 14), (32, 10), (29, 18), (22, 20), (9, 20), (4, 16)]
    pygame.draw.polygon(s, wood, hull)
    pygame.draw.line(s, dark, (7, 17), (28, 17))
    pygame.draw.line(s, light, (3, 11), (31, 11))
    pygame.draw.line(s, pal["B"], (6, 12), (28, 12))
    for hx in (7, 12, 17, 22):                                                               # soldiers sitting shoulder to shoulder
        bob = 1 if (hx // 5 + frame) % 3 == 0 else 0
        pygame.draw.rect(s, pal["h"], (hx, 5 + bob, 4, 3))
        pygame.draw.rect(s, pal["s"], (hx + 1, 8 + bob, 2, 1))
        pygame.draw.rect(s, pal["B"], (hx, 9 + bob, 4, 3))
    for sx in (8, 13, 18, 23):                                                               # shields along the rail
        pygame.draw.circle(s, pal["y"] if (sx // 5) % 2 else pal["B"], (sx + 1, 13), 2)
        s.set_at((sx + 1, 13), pal["h"])
    pygame.draw.line(s, dark, (29, 11), (30, 3))                                             # a banner on the prow
    pygame.draw.polygon(s, pal["B"], [(30, 3), (34, 4), (30, 6)])
    pygame.draw.polygon(s, dark, [(2, 11), (1, 8), (4, 8), (4, 11)])                         # the stern post
    _oars(s, white, (11, 17, 23), 14, frame)
    return outlined(s)



def huorn(white=False):
    s = pygame.Surface((13, 17), pygame.SRCALPHA)
    dark = (255, 255, 255) if white else (28, 62, 34)
    mid = (255, 255, 255) if white else (46, 92, 50)
    light = (255, 255, 255) if white else (82, 138, 72)
    bark = (255, 255, 255) if white else (82, 58, 36)
    pygame.draw.rect(s, bark, (5, 9, 3, 8))
    pygame.draw.ellipse(s, dark, (0, 0, 13, 12))
    pygame.draw.ellipse(s, mid, (1, 1, 10, 8))
    pygame.draw.ellipse(s, light, (3, 2, 5, 4))
    s.set_at((4, 6), (230, 244, 130))
    s.set_at((8, 6), (230, 244, 130))
    return outlined(s)


CATAPULT_ARM = (160, 190, 235, 275, 320, 350)       # throwing-arm angle (degrees, y down) for poses 0..5: cocked back ... flung
TREBUCHET_ARM = (40, 8, -35, -80, -120, -150)       # long-arm angle for poses 0..5: down behind ... flung up and over


def catapult(color, white=False, pose=0):
    """A catapult. pose 0 has the arm cocked back with a stone in the bucket; poses 1 to 5 swing it up and over."""
    s = pygame.Surface((18, 16), pygame.SRCALPHA)
    wood = (255, 255, 255) if white else (140, 98, 52)
    dark = (255, 255, 255) if white else (78, 52, 30)
    light = (255, 255, 255) if white else (186, 140, 84)
    pygame.draw.rect(s, wood, (1, 11, 16, 2))
    pygame.draw.rect(s, light, (1, 11, 16, 1))
    for cx in (4, 14):                                      # spoked wheels
        pygame.draw.circle(s, dark, (cx, 13), 3)
        pygame.draw.circle(s, wood, (cx, 13), 1)
    pygame.draw.rect(s, wood, (8, 5, 2, 7))                 # the upright
    ang = math.radians(CATAPULT_ARM[max(0, min(5, pose))])
    px, py = 9, 5
    tx, ty = round(px + 7 * math.cos(ang)), round(py + 7 * math.sin(ang))
    pygame.draw.line(s, dark, (px, py), (tx, ty), 2)        # the throwing arm
    pygame.draw.rect(s, dark, (tx - 1, ty - 1, 3, 3))       # the bucket
    if pose <= 2:                                           # the stone, until it is thrown
        s.set_at((tx, ty - 1), (255, 255, 255) if white else (150, 150, 156))
        s.set_at((tx + 1, ty - 1), (255, 255, 255) if white else (120, 120, 126))
    pygame.draw.polygon(s, color if not white else (255, 255, 255), [(13, 4), (17, 5), (13, 8)])
    return outlined(s)


def trebuchet(color, white=False, pose=0):
    """A trebuchet. pose 0 has the long arm drawn down with a stone in its sling and the counterweight raised;
    poses 1 to 5 let the weight fall and fling the arm up and over."""
    s = pygame.Surface((22, 22), pygame.SRCALPHA)
    wood = (255, 255, 255) if white else (126, 88, 46)
    dark = (255, 255, 255) if white else (70, 46, 26)
    light = (255, 255, 255) if white else (184, 138, 82)
    pygame.draw.rect(s, wood, (0, 18, 22, 2))
    pygame.draw.rect(s, light, (0, 18, 22, 1))
    for cx in (3, 18):
        pygame.draw.circle(s, dark, (cx, 19), 2)
    px, py = 11, 9
    pygame.draw.line(s, wood, (6, 18), (px, py), 2)                        # the A-frame's two legs
    pygame.draw.line(s, wood, (16, 18), (px, py), 2)
    ang = math.radians(TREBUCHET_ARM[max(0, min(5, pose))])
    lx, ly = round(px + 10 * math.cos(ang)), round(py + 10 * math.sin(ang))   # the long arm's end
    sx, sy = round(px - 4 * math.cos(ang)), round(py - 4 * math.sin(ang))     # the short arm's end: the weight hangs here
    pygame.draw.line(s, dark, (px, py), (lx, ly), 2)
    pygame.draw.line(s, dark, (px, py), (sx, sy), 2)
    pygame.draw.rect(s, dark, (sx - 2, sy, 5, 5))                           # the counterweight box
    pygame.draw.rect(s, light, (sx - 2, sy, 5, 1))
    if pose <= 2:                                                           # the stone in its sling
        pygame.draw.line(s, dark, (lx, ly), (lx + (1 if lx < px else -1), ly + 2))
        pygame.draw.circle(s, (255, 255, 255) if white else (150, 150, 156), (lx, ly + 2), 1)
    pygame.draw.polygon(s, color if not white else (255, 255, 255), [(px, 3), (px + 5, 4), (px, 6)])
    return outlined(s)


# The siege engines are drawn large and in each side's style by siege_art.py; these replace the small ones above.
from siege_art import ballista, catapult, mangonel, ram_crew, siege_tower, trebuchet  # noqa: E402,F401,F811

SIEGE_KINDS = ("catapult", "trebuchet", "ballista", "mangonel", "ram_crew", "siege_tower")


# ---------------------------------------------------------------------------------------------- each side's own look
STEEL = {  # the grey steel tones of the shared art -> each side's metal: Greek bronze, Roman legionary iron
    "ravensmere": {(128, 132, 146): (178, 130, 62), (206, 210, 222): (242, 202, 112), (74, 76, 90): (112, 76, 34)},
    "ironvale": {(128, 132, 146): (148, 152, 166), (206, 210, 222): (224, 228, 236), (74, 76, 90): (82, 84, 100)},
}
DRESSED = ("foot", "archer", "longbow", "halberdier", "berserker", "pavise_cross", "rider")
BONE, FEATHER = (230, 224, 204), (246, 246, 255)


def dress(s, kind, style):
    """Gives the shared foot-soldier art a side's look: the Greeks (Ravensmere) have bronze and a tall blue horsehair
    crest, the Romans (Ironvale) legionary iron and a scarlet transverse crest. Returns a new surface (a little bigger, for the crest)."""
    if not style or style not in STEEL or kind not in DRESSED:
        return s
    w, h = s.get_size()
    out = pygame.Surface((w + 6, h + 5), pygame.SRCALPHA)
    ox, oy = 3, 4
    swap = STEEL[style]
    for y in range(h):
        for x in range(w):
            c = s.get_at((x, y))
            if c.a:
                rgb = swap.get((c.r, c.g, c.b))
                out.set_at((x + ox, y + oy), (*rgb, c.a) if rgb else c)
    ink = tuple(INK)
    top = next((y for y in range(h) if any(tuple(s.get_at((x, y)))[:3] != ink and s.get_at((x, y)).a for x in range(w))), 0)
    xs = [x for y in (top, top + 1) for x in range(w) if s.get_at((x, y)).a and tuple(s.get_at((x, y)))[:3] != ink]
    if not xs:
        return out
    x0, x1 = min(xs) + ox, max(xs) + ox
    ty = top + oy
    if kind == "rider":                                  # a horse and rider: just the metal, no crest
        return out
    cx = (x0 + x1) // 2
    pts = []
    if style == "ironvale":                              # a legionary's galea: a scarlet transverse crest fanned over the helm
        red, redl = (176, 38, 34), (222, 70, 58)
        for x in range(x0, x1 + 1):
            pts.append((x, ty - 1, red))
        for x in range(x0 - 1, x1 + 2):
            pts.append((x, ty - 2, redl if x % 2 else red))
        pts += [(cx, ty - 3, redl), (cx + 1, ty - 3, red), (x0, ty, (226, 188, 70))]     # and a brass brow-band
    else:                                                # a hoplite's Corinthian helm: a tall horsehair crest streaming back
        blue, bluel = (52, 94, 200), (150, 188, 250)
        for x in range(x0, x1 + 1):
            pts.append((x, ty - 1, blue))
        pts += [(cx - 1, ty - 2, bluel), (cx, ty - 2, bluel), (cx + 1, ty - 2, bluel), (cx, ty - 3, bluel),
                (x0 - 1, ty, blue), (x0 - 1, ty + 1, blue), (x0 - 2, ty + 1, blue), (x0 - 2, ty + 2, bluel)]
    for px, py, _ in pts:                                # an ink outline round each added pixel
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if 0 <= px + dx < out.get_width() and 0 <= py + dy < out.get_height() and not out.get_at((px + dx, py + dy)).a:
                out.set_at((px + dx, py + dy), INK)
    for px, py, col in pts:
        if 0 <= px < out.get_width() and 0 <= py < out.get_height():
            out.set_at((px, py), col)
    return out


# ---------------------------------------------------------------------------------------------- flyers and ships, per side
def _rgb(r, g, b):
    return (r, g, b)


RESTYLE = {
    # kind -> style -> {the shared art's colour: this side's colour}.  Greek: white marble, blue and gold.  Roman: scarlet, iron, gold.
    "wyvern": {"ravensmere": {(92, 112, 78): (190, 208, 226), (170, 168, 120): (246, 236, 200), (52, 66, 46): (84, 112, 168)},
               "ironvale": {(92, 112, 78): (150, 44, 40), (170, 168, 120): (228, 190, 76), (52, 66, 46): (80, 22, 26),
                            (255, 210, 60): (255, 90, 40)}},
    "hawk": {"ravensmere": {(124, 88, 56): (222, 224, 232), (78, 54, 34): (132, 142, 176)},
             "ironvale": {(124, 88, 56): (96, 62, 42), (78, 54, 34): (54, 34, 26), (240, 234, 220): (246, 242, 230),
                          (255, 200, 40): (255, 214, 80)}},
    "griffon": {"ravensmere": {(196, 150, 78): (240, 226, 176), (150, 106, 52): (206, 180, 120), (104, 70, 36): (150, 122, 76)},
                "ironvale": {(196, 150, 78): (184, 58, 48), (150, 106, 52): (128, 38, 38), (104, 70, 36): (78, 24, 28),
                             (244, 238, 222): (240, 232, 212), (255, 200, 40): (255, 216, 84)}},
    "harpy": {"ravensmere": {(118, 96, 84): (214, 222, 242), (76, 58, 52): (136, 156, 198), (44, 34, 34): (244, 230, 176)},
              "ironvale": {(118, 96, 84): (176, 62, 54), (76, 58, 52): (116, 36, 38), (44, 34, 34): (226, 190, 74)}},
}
_SHIP_WOOD = {
    "ravensmere": {(128, 90, 50): (206, 176, 126), (84, 58, 34): (126, 92, 56), (176, 132, 78): (240, 216, 164),
                   (128, 132, 146): (178, 130, 62)},
    "ironvale": {(128, 90, 50): (122, 68, 46), (84, 58, 34): (62, 36, 28), (176, 132, 78): (170, 104, 70),
                 (128, 132, 146): (150, 154, 168)},
}
for _k in ("longship", "galley", "catapult_ship", "landing_boat"):
    RESTYLE[_k] = _SHIP_WOOD

# bits added on top: (x, y, colour) pixels, in the outlined sprite's coordinates
OVERLAY = {
    ("wyvern", "ironvale"): [(9, 7, (226, 190, 76)), (12, 6, (226, 190, 76)), (15, 6, (226, 190, 76)),     # gilt dorsal plates
                             (26, 9, (176, 38, 34)), (26, 8, (222, 70, 58))],                              # a scarlet crest on the head
    ("wyvern", "ravensmere"): [(14, 1, (255, 224, 120)), (16, 1, (255, 224, 120)), (15, 0, (255, 224, 120))],    # a gilded diadem
    ("hawk", "ironvale"): [(14, 8, (176, 38, 34)), (13, 8, (176, 38, 34))],                                  # a scarlet neck-band
    ("hawk", "ravensmere"): [(23, 8, (255, 224, 120)), (22, 8, (255, 224, 120))],                            # gold at the beak
    ("griffon", "ironvale"): [(24, 4, (226, 190, 76)), (25, 3, (226, 190, 76)), (21, 4, (226, 190, 76))],    # a gold aquila crest
    ("griffon", "ravensmere"): [(26, 3, (255, 236, 160)), (27, 4, (255, 236, 160))],                         # a golden crest
    ("harpy", "ironvale"): [(20, 9, (226, 190, 74)), (19, 9, (226, 190, 74))],                               # gold armlets
    ("harpy", "ravensmere"): [(11, 1, (126, 184, 92)), (12, 1, (126, 184, 92)), (13, 1, (126, 184, 92))],    # a laurel wreath
    ("longship", "ravensmere"): [(43, 8, (244, 244, 252)), (44, 8, (60, 110, 210)), (44, 9, (20, 20, 40)),   # a painted eye on the bow
                                 (43, 9, (244, 244, 252)), (43, 16, (214, 158, 74)), (44, 16, (214, 158, 74)),
                                 (45, 16, (246, 206, 120)), (43, 17, (160, 112, 50)), (44, 17, (160, 112, 50))],   # a bronze ram
    ("longship", "ironvale"): [(43, 16, (170, 174, 186)), (44, 16, (170, 174, 186)), (45, 16, (222, 226, 234)),  # an iron ram
                               (43, 17, (110, 112, 126)), (44, 17, (110, 112, 126)),
                               (43, 8, (226, 190, 70)), (44, 8, (226, 190, 70)), (44, 9, (176, 38, 34))],    # a gilt prow ornament
    ("galley", "ironvale"): [(x, 19, (178, 40, 36)) for x in range(8, 46, 4)] + [(x, 20, (226, 190, 70)) for x in range(8, 46, 4)],  # scuta along the rail
    ("galley", "ravensmere"): [(x, 20, (255, 224, 120)) for x in range(6, 46, 6)] + [(x, 19, (60, 110, 210)) for x in range(6, 46, 6)],  # round shields
}


def restyle(s, kind, style):
    """Gives a flyer or a ship its side's look: the kingdom's pale, gilded creatures and pale-oak ships, the north's
    dark, red-eyed beasts and black-timber ships with iron spikes. Works on a copy (the renderer skips it for a white hit-flash)."""
    maps = RESTYLE.get(kind, {}).get(style)
    if maps is None:
        return s
    out = s.copy()
    w, h = out.get_size()
    for y in range(h):
        for x in range(w):
            c = out.get_at((x, y))
            if c.a:
                new = maps.get((c.r, c.g, c.b))
                if new:
                    out.set_at((x, y), (*new, c.a))
    for x, y, col in OVERLAY.get((kind, style), ()):
        if 0 <= x < w and 0 <= y < h:
            out.set_at((x, y), col)
    return out
