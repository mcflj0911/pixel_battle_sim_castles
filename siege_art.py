"""Siege engines drawn large (a catapult is now twice the size of a foot soldier's height), and in two styles: the
Greek (ravensmere) engines of pale olive wood with bronze fittings and meander-edged shields in the side's colour, and
Roman (ironvale) engines of dark oak and iron with scarlet hides, scuta and vexillum banners. Every function takes
(colour, white, pose, style) and returns a finished sprite facing right. `white` paints it all white (the hit flash).
Used by sprites.py, which re-exports the names; the renderer passes the style of the side that owns the engine."""
import math

import pygame

INK = (22, 16, 14)

LOOK = {
    # Greek: pale olive-wood and whitewash, bronze fittings, blue paint.  Roman: dark oak, iron, scarlet hides, brass.
    "ravensmere": dict(wood=(184, 146, 92), dark=(104, 76, 44), light=(236, 204, 142), iron=(204, 150, 70),
                       irond=(142, 98, 44), rope=(232, 222, 188), stone=(206, 204, 198), stoned=(150, 148, 144),
                       hide=(226, 220, 204), hided=(176, 168, 150), trim=(250, 250, 255), fire=(255, 150, 40)),
    "ironvale": dict(wood=(112, 74, 46), dark=(54, 36, 26), light=(158, 110, 70), iron=(156, 160, 172),
                     irond=(84, 86, 98), rope=(170, 142, 100), stone=(120, 118, 122), stoned=(74, 72, 78),
                     hide=(150, 52, 44), hided=(100, 32, 30), trim=(226, 188, 70), fire=(255, 120, 30)),
}


def _look(style, white):
    k = LOOK.get(style, LOOK["ravensmere"])
    if white:
        return {n: (255, 255, 255) for n in k}
    return k


def _shade(c, k):
    return tuple(max(0, min(255, int(v * k))) for v in c)


def _outlined(s, col=INK):
    w, h = s.get_size()
    out = pygame.Surface((w + 2, h + 2), pygame.SRCALPHA)
    m = pygame.mask.from_surface(s).to_surface(setcolor=col, unsetcolor=(0, 0, 0, 0))
    for dx, dy in ((0, 1), (2, 1), (1, 0), (1, 2)):
        out.blit(m, (dx, dy))
    out.blit(s, (1, 1))
    return out


def _r(s, c, x, y, w, h):
    pygame.draw.rect(s, c, (x, y, w, h))


def _beam(s, k, x, y, w, h):
    """A timber: its colour with a lit top edge and a dark bottom edge."""
    _r(s, k["wood"], x, y, w, h)
    _r(s, k["light"], x, y, w, 1)
    if h > 2:
        _r(s, k["dark"], x, y + h - 1, w, 1)


def _wheel(s, k, cx, cy, r, style):
    pygame.draw.circle(s, k["dark"], (cx, cy), r)
    pygame.draw.circle(s, k["wood"], (cx, cy), r - 1)
    for a in range(0, 180, 45):                                            # spokes
        dx, dy = round((r - 1) * math.cos(math.radians(a))), round((r - 1) * math.sin(math.radians(a)))
        pygame.draw.line(s, k["dark"], (cx - dx, cy - dy), (cx + dx, cy + dy))
    pygame.draw.circle(s, k["iron"], (cx, cy), max(1, r // 3))
    if style == "ironvale":                                                # studded rims
        for a in range(0, 360, 60):
            px, py = cx + round(r * math.cos(math.radians(a))), cy + round(r * math.sin(math.radians(a)))
            if 0 <= px < s.get_width() and 0 <= py < s.get_height():
                s.set_at((px, py), k["iron"])


def _pennant(s, k, color, white, x, y, style, length=7):
    """A banner on a short pole: the side's colour, with a white stripe (kingdom) or a black one (north)."""
    c = (255, 255, 255) if white else color
    pygame.draw.line(s, k["dark"], (x, y), (x, y + length + 2))
    if style == "ironvale":                                                # a Roman vexillum: a square cloth hung from a crossbar
        _r(s, k["trim"], x, y, length, 1)
        _r(s, c, x + 1, y + 1, length - 2, 5)
        _r(s, k["trim"], x + 1, y + 3, length - 2, 1)                      # a gold band
        for fx in range(x + 1, x + length - 1, 2):                         # the fringe
            s.set_at((fx, y + 6), k["trim"])
    else:                                                                  # a Greek streamer with a gilded spear-tip
        pygame.draw.polygon(s, c, [(x, y), (x + length, y + 2), (x, y + 5)])
        _r(s, k["trim"], x + 1, y + 2, length - 3, 1)
        s.set_at((x, y - 1), (255, 220, 110))


def _shield_plate(s, k, color, white, x, y, w, h, style):
    """A mantlet along the frame: painted wood in the side's colour (kingdom) or riveted iron plate (north)."""
    if style == "ironvale":                                                # scutum: scarlet, gold-edged, with a brass boss
        _r(s, (255, 255, 255) if white else (178, 40, 36), x, y, w, h)
        _r(s, k["trim"], x, y, w, 1)
        _r(s, k["trim"], x, y + h - 1, w, 1)
        for rx in range(x + 2, x + w - 2, 5):
            _r(s, k["trim"], rx, y + h // 2 - 1, 2, 2)
    else:                                                                  # Greek: the side's colour with a white meander border
        _r(s, (255, 255, 255) if white else color, x, y, w, h)
        for mx in range(x, x + w, 2):
            s.set_at((mx, y), k["trim"])
        _r(s, _shade(color, 0.6) if not white else (255, 255, 255), x, y + h - 1, w, 1)
        s.set_at((x + w // 2, y + h // 2), (255, 220, 110) if not white else (255, 255, 255))


# ============================================================================================ catapult
CATAPULT_ARM = (160, 190, 235, 275, 320, 350)       # throwing-arm angle (degrees, y down) for poses 0..5: cocked back ... flung


def catapult(color, white=False, pose=0, style=""):
    """A catapult on a long timber frame with spoked wheels, a windlass at the back and a stone in the bucket."""
    k = _look(style, white)
    s = pygame.Surface((38, 28), pygame.SRCALPHA)
    _beam(s, k, 2, 17, 34, 3)                                              # the two long frame timbers
    _beam(s, k, 2, 20, 34, 2)
    for bx in (6, 17, 29):                                                 # cross-ties
        _r(s, k["dark"], bx, 16, 2, 7)
    _shield_plate(s, k, color, white, 22, 12, 12, 5, style)                # a mantlet on the front of the frame
    for cx in (9, 29):
        _wheel(s, k, cx, 23, 5, style)
    # the windlass at the back, with the rope that draws the arm down
    pygame.draw.circle(s, k["dark"], (5, 14), 3)
    pygame.draw.circle(s, k["rope"], (5, 14), 2)
    pygame.draw.line(s, k["dark"], (2, 14), (8, 14))
    # the two uprights, braced, and the axle the arm turns on
    px, py = 17, 8
    for ux in (15, 19):
        _r(s, k["wood"], ux, py, 2, 10)
        _r(s, k["light"], ux, py, 1, 10)
    pygame.draw.line(s, k["dark"], (14, 17), (18, py + 1))
    pygame.draw.line(s, k["dark"], (21, 17), (17, py + 1))
    _r(s, k["iron"], 14, py - 1, 7, 2)                                     # the iron-bound axle
    ang = math.radians(CATAPULT_ARM[max(0, min(5, pose))])
    L = 17
    tx, ty = round(px + L * math.cos(ang)), round(py + L * math.sin(ang))
    pygame.draw.line(s, k["dark"], (px, py), (tx, ty), 3)                  # the throwing arm
    pygame.draw.line(s, k["wood"], (px, py - 1), (tx, ty - 1))
    if pose <= 2:
        pygame.draw.line(s, k["rope"], (5, 14), (tx, ty))                  # drawn down by the windlass rope
    bx, by = tx - 3, ty - 2                                                # the bucket
    if style == "ironvale":
        pygame.draw.polygon(s, k["irond"], [(bx, by), (bx + 6, by), (bx + 5, by + 4), (bx + 1, by + 4)])
        _r(s, k["trim"], bx, by - 1, 6, 1)                                 # a brass rim
    else:
        _r(s, k["dark"], bx, by, 6, 4)
        _r(s, k["rope"], bx, by, 6, 1)                                     # a wicker bucket
        _r(s, k["iron"], bx, by + 3, 6, 1)
    if pose <= 2:                                                          # the stone, until it is thrown
        pygame.draw.circle(s, k["stone"], (bx + 3, by - 1), 3)
        pygame.draw.circle(s, k["stoned"], (bx + 4, by), 1)
    _pennant(s, k, color, white, 33, 4, style)
    return _outlined(s)


# ============================================================================================ trebuchet
TREBUCHET_ARM = (40, 8, -35, -80, -120, -150)       # long-arm angle for poses 0..5: down behind ... flung up and over


def trebuchet(color, white=False, pose=0, style=""):
    """A trebuchet: a tall A-frame on a heavy base, a long arm and a counterweight box of stones."""
    k = _look(style, white)
    s = pygame.Surface((48, 46), pygame.SRCALPHA)
    _beam(s, k, 1, 36, 46, 3)                                              # the base timbers
    _beam(s, k, 4, 39, 40, 2)
    for cx in (8, 40):
        _wheel(s, k, cx, 41, 4, style)
    px, py = 23, 14
    for x0 in (11, 36):                                                    # the A-frame: two pairs of leaning legs
        pygame.draw.line(s, k["wood"], (x0, 37), (px, py), 3)
        pygame.draw.line(s, k["light"], (x0 - 1, 37), (px - 1, py))
    pygame.draw.line(s, k["dark"], (14, 28), (33, 28), 2)                  # cross-bracing
    pygame.draw.line(s, k["dark"], (14, 28), (30, 37))
    pygame.draw.line(s, k["dark"], (33, 28), (17, 37))
    _r(s, k["iron"], px - 3, py - 1, 7, 3)                                 # the axle and its iron cap
    ang = math.radians(TREBUCHET_ARM[max(0, min(5, pose))])
    lx, ly = round(px + 22 * math.cos(ang)), round(py + 22 * math.sin(ang))     # the long arm's end
    sx, sy = round(px - 7 * math.cos(ang)), round(py - 7 * math.sin(ang))       # the short arm's end: the weight
    pygame.draw.line(s, k["dark"], (px, py), (lx, ly), 3)
    pygame.draw.line(s, k["wood"], (px, py - 1), (lx, ly - 1))
    pygame.draw.line(s, k["dark"], (px, py), (sx, sy), 3)
    wx0, wy0 = sx - 5, sy                                                  # the counterweight box, hung from the short arm
    _r(s, k["dark"], wx0, wy0, 11, 10)
    _r(s, k["wood"], wx0 + 1, wy0 + 1, 9, 8)
    _r(s, k["iron"], wx0, wy0, 11, 1)
    _r(s, k["iron"], wx0, wy0 + 9, 11, 1)
    for rx, ry in ((2, 3), (6, 3), (4, 6), (8, 6)):                        # stones showing in the box
        _r(s, k["stone"], wx0 + rx, wy0 + ry, 2, 2)
    if pose <= 2:                                                          # the stone in its sling
        sgn = 1 if lx < px else -1
        pygame.draw.line(s, k["rope"], (lx, ly), (lx + sgn * 2, ly + 5))
        pygame.draw.circle(s, k["stone"], (lx + sgn * 2, ly + 6), 3)
        pygame.draw.circle(s, k["stoned"], (lx + sgn * 2 + 1, ly + 7), 1)
    _pennant(s, k, color, white, px, 1, style, 8)
    return _outlined(s)


# ============================================================================================ ballista
def ballista(color, white=False, pose=0, style=""):
    """A great crossbow on a wheeled carriage, stock tilted at the sky. pose 0 has the string drawn with a bolt laid on
    it; poses 3 to 5 show the arms sprung forward and the bolt gone; poses 1 and 2 are the string released."""
    k = _look(style, white)
    s = pygame.Surface((34, 24), pygame.SRCALPHA)
    _beam(s, k, 2, 17, 28, 3)                                              # the carriage
    for cx in (8, 25):
        _wheel(s, k, cx, 20, 4, style)
    _r(s, k["wood"], 13, 11, 4, 7)                                         # the pedestal
    _r(s, k["dark"], 13, 11, 1, 7)
    pygame.draw.line(s, k["wood"], (4, 14), (24, 6), 3)                    # the stock, tilted up
    pygame.draw.line(s, k["light"], (4, 13), (24, 5))
    pygame.draw.line(s, k["dark"], (7, 16), (13, 12))                      # a brace under it
    drawn = pose <= 0 or pose >= 5                                         # string back (ready) or still winding
    held = pose <= 2
    ax, ay = (23, 6) if drawn else (24, 6)
    arm = 8 if drawn else 6
    top = (ax - (3 if drawn else 0), ay - arm)
    bot = (ax - (3 if drawn else 0), ay + arm + 1)
    _r(s, k["iron"], ax - 1, ay - 2, 4, 5)                                 # the iron-bound torsion frame
    _r(s, k["rope"], ax, ay - 1, 2, 3)
    pygame.draw.line(s, k["dark"], (ax + 1, ay), top, 3)                   # the two bow arms
    pygame.draw.line(s, k["dark"], (ax + 1, ay), bot, 3)
    sx = 15 if drawn else 27                                               # the bowstring
    cs = (255, 255, 255) if white else (236, 232, 214)
    pygame.draw.line(s, cs, top, (sx, ay))
    pygame.draw.line(s, cs, (sx, ay), bot)
    if held:                                                               # the bolt, laid ready
        pygame.draw.line(s, k["wood"], (sx, ay), (33, 1), 2)
        pygame.draw.polygon(s, k["iron"], [(33, 0), (31, 0), (33, 3)])
        _r(s, k["trim"], sx, ay - 1, 2, 2)
    _shield_plate(s, k, color, white, 8, 8, 6, 5, style)                   # a small shield on the pedestal
    _pennant(s, k, color, white, 3, 7, style, 6)
    return _outlined(s)


# ============================================================================================ mangonel
def mangonel(color, white=False, pose=0, style=""):
    """A mangonel: a squat frame with a skein of twisted rope across it, a long arm ending in a cup with a lit pot of
    pitch, and a barrel of pitch beside it. pose 0 has the arm drawn back; poses 1 to 5 fling it up and over."""
    k = _look(style, white)
    fire, fire2 = ((255, 255, 255),) * 2 if white else (k["fire"], (255, 226, 120))
    s = pygame.Surface((38, 28), pygame.SRCALPHA)
    _beam(s, k, 2, 18, 34, 3)
    _beam(s, k, 2, 21, 34, 2)
    for cx in (9, 29):
        _wheel(s, k, cx, 24, 5, style)
    for ux in (14, 21):                                                    # the two uprights ...
        _r(s, k["wood"], ux, 9, 3, 10)
        _r(s, k["light"], ux, 9, 1, 10)
    _r(s, k["rope"], 14, 8, 10, 5)                                         # ... and the twisted rope skein between them
    for bx in (15, 17, 19, 21, 23):
        pygame.draw.line(s, k["hided"], (bx, 8), (bx, 12))
    _r(s, k["iron"], 13, 7, 12, 1)
    px, py = 19, 9
    ang = math.radians(CATAPULT_ARM[max(0, min(5, pose))])
    tx, ty = round(px + 15 * math.cos(ang)), round(py + 15 * math.sin(ang))
    pygame.draw.line(s, k["dark"], (px, py), (tx, ty), 3)
    pygame.draw.line(s, k["wood"], (px, py - 1), (tx, ty - 1))
    if style == "ironvale":
        pygame.draw.polygon(s, k["irond"], [(tx - 3, ty - 1), (tx + 3, ty - 1), (tx + 2, ty + 3), (tx - 2, ty + 3)])
    else:
        _r(s, k["dark"], tx - 3, ty - 1, 6, 4)
        _r(s, k["iron"], tx - 3, ty + 2, 6, 1)
    if pose <= 2:                                                          # the pot of pitch, lit
        _r(s, (255, 255, 255) if white else (56, 50, 48), tx - 2, ty - 4, 4, 3)
        _r(s, k["irond"], tx - 2, ty - 4, 4, 1)
        s.set_at((tx, ty - 6), fire)
        s.set_at((tx + 1, ty - 7), fire2)
        s.set_at((tx, ty - 7), fire)
        s.set_at((tx - 1, ty - 5), fire)
    _r(s, k["dark"], 29, 12, 6, 7)                                         # a barrel of pitch ...
    _r(s, k["wood"], 30, 13, 4, 5)
    _r(s, k["iron"], 29, 14, 6, 1)
    _r(s, k["iron"], 29, 17, 6, 1)
    s.set_at((31, 11), fire)                                               # ... smouldering
    s.set_at((32, 10), fire2)
    _shield_plate(s, k, color, white, 3, 13, 8, 5, style)
    _pennant(s, k, color, white, 4, 3, style, 6)
    return _outlined(s)


# ============================================================================================ battering ram
def ram_crew(color, white=False, frame=0, style=""):
    """A battering ram under a roofed shed on wheels: a hide roof with the side's stripe, the crew's legs showing below
    it, and a log with an iron head (a plain cap in the kingdom, a horned ram's skull in the north) that swings
    back and forth as they push."""
    k = _look(style, white)
    s = pygame.Surface((62, 32), pygame.SRCALPHA)
    sw = 3 if frame % 2 else 0                                             # the log swings
    _r(s, k["dark"], 10 + sw, 18, 40, 4)                                   # the ram's log, hung under the roof
    _r(s, k["wood"], 10 + sw, 18, 40, 2)
    for cxx in (20, 34):
        _r(s, k["iron"], cxx + sw, 17, 2, 6)                               # iron bands
    hx = 49 + sw
    _r(s, k["iron"], hx, 16, 8, 8)                                         # the head
    _r(s, k["light"] if white else (214, 218, 230), hx, 16, 8, 1)
    pygame.draw.polygon(s, k["iron"], [(hx + 8, 16), (hx + 8, 23), (hx + 11, 20)])
    if style == "ravensmere":                                              # a bronze ram's head (krios), horns curling back
        bz = (255, 255, 255) if white else (214, 158, 74)
        pygame.draw.line(s, bz, (hx + 1, 16), (hx - 2, 12), 2)
        pygame.draw.line(s, bz, (hx + 7, 16), (hx + 9, 12), 2)
    elif style == "ironvale":                                              # a Roman iron head with a scarlet-and-gold collar
        _r(s, (255, 255, 255) if white else (178, 40, 36), hx - 3, 17, 3, 6)
        _r(s, k["trim"], hx - 3, 17, 3, 1)
    for bx in (16, 26, 36, 45):                                            # the crew, seen under the eaves
        bob = 1 if (bx // 5 + frame) % 2 else 0
        _r(s, (255, 255, 255) if white else (226, 188, 148), bx, 16 + bob, 3, 3)
        _r(s, k["irond"] if white else _shade(color, 0.8), bx - 1, 19 + bob, 5, 4)
        _r(s, k["dark"], bx, 23, 2, 4 - bob)
        _r(s, k["dark"], bx + 3, 23, 2, 4 - bob)
    pygame.draw.polygon(s, k["hided"], [(4, 14), (9, 4), (47, 4), (53, 14)])           # the roof: hides on a frame
    pygame.draw.polygon(s, k["hide"], [(6, 13), (11, 5), (45, 5), (50, 13)])
    for rx in range(12, 46, 7):                                            # ribs
        pygame.draw.line(s, k["hided"], (rx, 5), (rx - 2, 13))
    _r(s, k["light"], 9, 4, 38, 1)
    for rx in range(14, 44, 9):                                            # scorch marks, or studs
        s.set_at((rx, 8), k["dark"])
    _shield_plate(s, k, color, white, 4, 13, 46, 3, style)                 # the side's stripe along the eaves
    _r(s, k["dark"], 4, 16, 2, 10)                                         # the posts
    _r(s, k["dark"], 48, 16, 2, 10)
    for cx in (10, 28, 45):                                                # the wheels
        _wheel(s, k, cx, 27, 4, style)
    pygame.draw.line(s, k["dark"], (27, 0), (27, 4))                       # a banner on the ridge
    _pennant(s, k, color, white, 27, 0, style, 7)
    return _outlined(s)


# ============================================================================================ siege tower
def siege_tower(color, white=False, pose=0, style=""):
    """A siege tower: a tall timber tower on wheels, armoured with hides, with three firing levels and archers at the
    openings. pose = 2 * (how many levels are manned, 0..3) + (1 while an archer is loosing). It faces right: the
    front (right side) carries the ramp and the openings."""
    k = _look(style, white)
    manned, firing = max(0, min(3, pose // 2)), pose % 2
    s = pygame.Surface((44, 76), pygame.SRCALPHA)
    # the base platform and wheels
    _beam(s, k, 2, 64, 40, 3)
    for cx in (8, 22, 36):
        _wheel(s, k, cx, 69, 5, style)
    # the tower body: a tapering box of hide-covered timber
    body = [(7, 64), (37, 64), (35, 12), (9, 12)]
    pygame.draw.polygon(s, k["hided"], body)
    pygame.draw.polygon(s, k["hide"], [(9, 62), (35, 62), (33, 14), (11, 14)])
    for yy in range(18, 62, 8):                                            # horizontal timber bands
        _r(s, k["dark"], 8 - (yy < 40), yy, 28 + 2 * (yy < 40), 2)
        _r(s, k["light"], 9, yy, 26, 1)
    for xx in (11, 21, 31):                                                # upright posts
        _r(s, k["wood"], xx, 14, 2, 49)
        _r(s, k["light"], xx, 14, 1, 49)
    # the three firing levels: an opening each, with an archer behind it
    for lvl, oy in enumerate((20, 34, 48)):
        _r(s, (14, 10, 12) if not white else (255, 255, 255), 22, oy, 12, 8)
        _r(s, k["dark"], 21, oy - 1, 14, 1)
        _r(s, k["dark"], 21, oy + 8, 14, 1)
        if lvl < manned and not white:
            ax = 25
            _r(s, (226, 188, 148), ax, oy + 2, 3, 3)                       # the archer's head
            _r(s, _shade(color, 0.9), ax - 1, oy + 5, 5, 3)                # his tunic
            _r(s, k["iron"], ax - 1, oy + 1, 5, 2)                         # a helm
            bow = 1 if firing else 0
            pygame.draw.line(s, k["wood"], (ax + 5 + bow, oy + 1), (ax + 5 + bow, oy + 7))   # the bow, drawn when firing
            if firing:
                _r(s, (255, 236, 160), ax + 7, oy + 4, 3, 1)               # the arrow leaving
            else:
                s.set_at((ax + 4, oy + 4), k["rope"])
    # the top: a crenellated fighting platform, with the side's banner
    _r(s, k["dark"], 5, 10, 34, 4)
    _r(s, k["wood"], 5, 10, 34, 2)
    for bx in range(5, 38, 6):
        _r(s, k["dark"], bx, 6, 4, 5)
        _r(s, k["light"], bx, 6, 4, 1)
    if style == "ironvale":                                                # a row of scarlet scuta along the battlements
        for bx in range(5, 38, 6):
            _r(s, (255, 255, 255) if white else (178, 40, 36), bx, 7, 4, 3)
            s.set_at((bx + 1, 8), k["trim"])
    else:                                                                  # a Greek pediment-like gilt rail
        _r(s, (255, 255, 255) if white else (255, 220, 110), 5, 9, 34, 1)
    # the boarding ramp, raised on the front of the tower
    pygame.draw.polygon(s, k["wood"], [(37, 62), (42, 60), (42, 16), (37, 14)])
    pygame.draw.line(s, k["light"], (37, 14), (37, 62))
    for yy in range(18, 60, 6):
        pygame.draw.line(s, k["dark"], (37, yy), (42, yy - 1))
    # the side's colours: shield mantlets on the lower body (or riveted plate), and a banner on a pole
    for sx in (11, 21):
        _shield_plate(s, k, color, white, sx, 56, 8, 7, style)
    pygame.draw.line(s, k["dark"], (22, 5), (22, 0))
    _pennant(s, k, color, white, 22, 0, style, 9)
    return _outlined(s)
