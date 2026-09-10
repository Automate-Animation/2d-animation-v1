#!/usr/bin/env python3
"""Build every layer of character_2 ("Teacher") as deterministic PIL vector art.

Run from core/:  python tools/build_character_2.py [--out images/characters/character_2]

Geometry contract (see docs/CHARACTER_2_NOTES.md):
  head 360x300 | eyes 250x130 @ head(55,62) | mouth 110x55 @ head(125,205)
  body 800x1080, head anchor -> head pasted at body(220,50) size (360,300)
Every PNG is drawn at SS x supersampling and downsampled for anti-aliasing.
"""
import argparse
import json
import math
import os
import shutil
import sys

from PIL import Image, ImageChops, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.constants import body_actions, emotions, screen_mode  # noqa: E402

SS = 4  # supersample factor

# ---- palette (named for meaning) ------------------------------------------
INK = (43, 33, 24, 255)
SKIN = (222, 170, 128, 255)
SKIN_SHADE = (196, 142, 102, 255)
HAIR = (59, 42, 32, 255)
DUPATTA = (233, 196, 106, 255)
DUPATTA_SHADE = (208, 168, 78, 255)
KAMEEZ = (42, 157, 143, 255)
KAMEEZ_SHADE = (32, 128, 118, 255)
SHALWAR = (244, 241, 222, 255)
SHOE = (70, 50, 40, 255)
WHITE = (255, 255, 255, 255)
IRIS = (78, 52, 36, 255)
LIP = (170, 70, 70, 255)
MOUTH_IN = (95, 20, 30, 255)
TONGUE = (226, 110, 120, 255)
BLUSH = (227, 160, 128, 255)  # skin pre-blended with pink (drawing translucent paint leaves grey)
TRANSPARENT = (0, 0, 0, 0)

# ---- canvas contract --------------------------------------------------------
HEAD_W, HEAD_H = 360, 300
EYES_W, EYES_H = 250, 130
EYES_POS = (55, 62)
MOUTH_W, MOUTH_H = 110, 55
MOUTH_POS = (125, 205)
BODY_W, BODY_H = 800, 1080
HEAD_ON_BODY = (220, 50)
NECK = (400, 350)
BODY_ON_BG = (560, 0)
ZOOM_POINT = (960, 200)
OUTLINE = 5  # px at 1x


class Canvas:
    """Supersampled RGBA drawing surface with 1x coordinates."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.im = Image.new("RGBA", (w * SS, h * SS), TRANSPARENT)
        self.d = ImageDraw.Draw(self.im)

    def s(self, pts):
        return [(x * SS, y * SS) for x, y in pts]

    def ellipse(self, cx, cy, rx, ry, fill, outline=INK, width=OUTLINE):
        box = [(cx - rx) * SS, (cy - ry) * SS, (cx + rx) * SS, (cy + ry) * SS]
        self.d.ellipse(box, fill=fill, outline=outline, width=width * SS if outline else 0)

    def poly(self, pts, fill, outline=INK, width=OUTLINE):
        self.d.polygon(self.s(pts), fill=fill, outline=outline, width=width * SS if outline else 0)

    def line(self, pts, fill=INK, width=OUTLINE):
        self.d.line(self.s(pts), fill=fill, width=width * SS, joint="curve")
        r = width * SS / 2
        for x, y in self.s(pts):  # round caps
            self.d.ellipse([x - r, y - r, x + r, y + r], fill=fill)

    def thick_segment(self, a, b, width, fill, outline=INK, ow=OUTLINE):
        """Capsule-shaped limb: outline first, then fill inset."""
        self.line([a, b], fill=outline, width=width + 2 * ow)
        self.line([a, b], fill=fill, width=width)

    def arc(self, cx, cy, rx, ry, start, end, fill=INK, width=OUTLINE):
        box = [(cx - rx) * SS, (cy - ry) * SS, (cx + rx) * SS, (cy + ry) * SS]
        self.d.arc(box, start, end, fill=fill, width=width * SS)

    def chord_fill(self, cx, cy, rx, ry, start, end, fill):
        box = [(cx - rx) * SS, (cy - ry) * SS, (cx + rx) * SS, (cy + ry) * SS]
        self.d.chord(box, start, end, fill=fill)

    def paste(self, other, xy):
        self.im.alpha_composite(other.im, (xy[0] * SS, xy[1] * SS))

    def save(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.im.resize((self.w, self.h), Image.LANCZOS).save(path)


def bezier(p0, p1, p2, p3, n=24):
    out = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        x = u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0]
        y = u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1]
        out.append((x, y))
    return out


# ============================================================ HEAD ==========
def draw_head(direction):
    """direction in L/M/R. Eyes & mouth zones are identical for all three; the
    turn is expressed by the dupatta/hair volume, ear and nose offsets only."""
    c = Canvas(HEAD_W, HEAD_H)
    turn = {"L": -1, "M": 0, "R": 1}[direction]
    cx, cy = 180, 150
    # neck (behind everything, runs to canvas bottom so it overlaps the collar)
    c.poly([(150, 240), (210, 240), (214, HEAD_H + 8), (146, HEAD_H + 8)], SKIN_SHADE)
    # dupatta outer volume: shifted opposite to the turn so more "back of head" shows
    dx = -turn * 14
    c.ellipse(cx + dx, cy + 4, 140, 148, DUPATTA)
    c.chord_fill(cx + dx, cy + 4, 140, 148, 20, 160, DUPATTA_SHADE)  # lower shade
    c.ellipse(cx + dx, cy + 4, 140, 148, None, INK, OUTLINE)
    # ear on the far side of the turn
    if turn != 0:
        ex = cx - turn * 126
        c.ellipse(ex, 150, 14, 20, SKIN)
    # face
    c.ellipse(cx, cy, 118, 138, SKIN)
    # hair: top chord of the face oval (fringe shows between dupatta band and brows)
    c.chord_fill(cx, cy, 118, 138, 215, 325, HAIR)
    c.ellipse(cx, cy, 118, 138, None, INK, OUTLINE)
    # dupatta edge framing the face (drawn over hair)
    frame = bezier((cx - 118, 160), (cx - 125, 10), (cx + 125, 10), (cx + 118, 160))
    c.line(frame, fill=DUPATTA, width=22)
    c.line(frame, fill=INK, width=4)
    # blush
    c.ellipse(cx - 70, 200, 22, 12, BLUSH, None)
    c.ellipse(cx + 70, 200, 22, 12, BLUSH, None)
    # nose (offset with turn)
    nx = cx + turn * 10
    c.line([(nx - 6, 168), (nx + 4, 190), (nx - 10, 194)], fill=INK, width=4)
    return c


# ============================================================ EYES ==========
# parameter dictionary per emotion: openness (0..1), brow (inner_dy, outer_dy, thickness),
# pupil scale, lower-lid squint (0..1), per-eye overrides for asymmetry, pupil dx bias
EMO = {
    "happy":      dict(open=1.0, brow=(-4, -8), pupil=1.0, squint=0.35),
    "sad":        dict(open=0.75, brow=(-16, 4), pupil=1.0, squint=0.0, lid_out=0.35),
    "angry":      dict(open=0.7, brow=(10, -14), pupil=0.9, squint=0.0, lid_in=0.45),
    "bore":       dict(open=0.5, brow=(0, 0), pupil=1.0, squint=0.0),
    "content":    dict(open=0.8, brow=(-2, -6), pupil=1.0, squint=0.55),
    "glare":      dict(open=0.45, brow=(6, -4), pupil=0.9, squint=0.0),
    "sarcasm":    dict(open=0.8, brow=(-2, -6), pupil=1.0, squint=0.0,
                       right=dict(open=0.5, brow=(4, 2))),
    "worried":    dict(open=1.0, brow=(-20, -2), pupil=0.8, squint=0.0),
    "crazy":      dict(open=1.0, brow=(-14, 8), pupil=0.6, squint=0.0,
                       right=dict(pupil=1.3, brow=(8, -12))),
    "evil_laugh": dict(open=0.55, brow=(12, -18), pupil=0.8, squint=0.5),
    "lust":       dict(open=0.6, brow=(-10, -14), pupil=1.2, squint=0.2),
    "shock":      dict(open=1.15, brow=(-18, -20), pupil=0.55, squint=0.0),
    "silly":      dict(open=1.0, brow=(-6, -14), pupil=1.0, squint=0.2, cross=1,
                       right=dict(open=0.7)),
    "spoked":     dict(open=1.15, brow=(-22, -12), pupil=0.5, squint=0.0,
                       right=dict(brow=(-6, -26), pupil=0.4)),  # asymmetric so it is not a shock clone
}


def intensify(p):
    q = dict(p)
    q["open"] = max(0.3, min(1.25, 1 + (p["open"] - 1) * 1.6)) if p["open"] != 1 else p["open"] * 1.05  # floor: keep a pupil visible so bore_2/glare_2/sarcasm_2 stay distinct
    q["brow"] = (p["brow"][0] * 1.6, p["brow"][1] * 1.6)
    q["pupil"] = 1 + (p["pupil"] - 1) * 1.6
    q["squint"] = min(1.0, p["squint"] * 1.6)
    for k in ("lid_in", "lid_out"):
        if k in p:
            q[k] = min(0.45, p[k] * 1.3)
    if "right" in p:
        q["right"] = intensify({**{"open": 1, "brow": (0, 0), "pupil": 1, "squint": 0}, **p["right"]})
        q["right"] = {k: q["right"][k] for k in p["right"]}
    return q


def draw_eye(c, ex, ey, p, look_dx, blink=None, side=+1):
    """One eye centred (ex,ey). side=+1 for character-left (viewer right), -1 other.
    blink: None | 'half' | 'closed'. Eyelids are done by MASKING the eyeball (never by
    painting skin-coloured patches, which leave visible rectangles after anti-aliasing)."""
    rx, ry = 30, 32
    open_ = p["open"] if blink is None else (0.45 if blink == "half" else 0.0)
    if blink == "closed" or open_ <= 0.05:
        c.line([(ex - rx, ey + 4), (ex - rx * 0.5, ey + 12), (ex, ey + 14),
                (ex + rx * 0.5, ey + 12), (ex + rx, ey + 4)], fill=INK, width=5)
    else:
        eye = Canvas(c.w, c.h)
        eye.ellipse(ex, ey, rx, ry, WHITE)
        pr = 15 * p["pupil"]
        pdx = look_dx + p.get("cross", 0) * (-10 * side)
        pdy = 0 if open_ >= 0.9 else 3
        eye.ellipse(ex + pdx, ey + pdy, pr, pr, IRIS, None)
        eye.ellipse(ex + pdx, ey + pdy, pr * 0.5, pr * 0.5, INK, None)
        eye.ellipse(ex + pdx - pr * 0.35, ey + pdy - pr * 0.4, pr * 0.22, pr * 0.22, WHITE, None)
        eye.ellipse(ex, ey, rx, ry, None, INK, OUTLINE)
        # lid geometry (1x coords)
        cover = (1 - min(open_, 1.0)) * 2 * ry
        lid_in = p.get("lid_in", 0) * 2 * ry
        lid_out = p.get("lid_out", 0) * 2 * ry
        top = ey - ry - 8
        inner_x, outer_x = ex - side * (rx + 8), ex + side * (rx + 8)
        lid_edge = [(outer_x, top + 8 + cover + lid_out), (ex, top + 8 + cover + (lid_in + lid_out) / 2),
                    (inner_x, top + 8 + cover + lid_in)]
        mask = Image.new("L", eye.im.size, 255)
        md = ImageDraw.Draw(mask)
        md.polygon(eye.s([(inner_x, top), (outer_x, top)] + lid_edge), fill=0)
        squint_edge = None
        if p["squint"] > 0:
            h = p["squint"] * 0.9 * ry
            bot = ey + ry + 8
            squint_edge = [(ex - rx - 8, bot - 8 - h * 0.4), (ex, bot - 8 - h), (ex + rx + 8, bot - 8 - h * 0.4)]
            md.polygon(eye.s([(ex - rx - 8, bot), (ex + rx + 8, bot)] + squint_edge[::-1]), fill=0)
        eye_alpha = eye.im.getchannel("A")
        eye.im.putalpha(ImageChops.multiply(eye_alpha, mask))
        c.im.alpha_composite(eye.im)
        # lid edge lines, clipped to the eyeball outline
        lines = Canvas(c.w, c.h)
        if cover + lid_in + lid_out > 2:
            lines.line(lid_edge, fill=INK, width=4)
        if squint_edge:
            lines.line(squint_edge, fill=INK, width=4)
        clip = Image.new("L", lines.im.size, 0)
        ImageDraw.Draw(clip).ellipse([(ex - rx - 1) * SS, (ey - ry - 1) * SS, (ex + rx + 1) * SS, (ey + ry + 1) * SS], fill=255)
        lines.im.putalpha(ImageChops.multiply(lines.im.getchannel("A"), clip))
        c.im.alpha_composite(lines.im)
    # brow: inner end towards the nose
    bi, bo = p["brow"]
    by = ey - ry - 14
    inner = (ex - side * 22, by + bi)
    outer = (ex + side * 30, by + bo)
    mid = ((inner[0] + outer[0]) / 2, min(inner[1], outer[1]) - 6)
    c.line(bezier(inner, mid, mid, outer, 12), fill=HAIR, width=8)


def draw_eyes(emotion, look, blink=None):
    base = EMO[emotion.replace("_2", "")]
    p = intensify(base) if emotion.endswith("_2") else base
    c = Canvas(EYES_W, EYES_H)
    look_dx = {"L": -10, "M": 0, "R": 10}[look]
    # canvas eye centres (70,78) and (180,78) -> head (125,140), (235,140)
    pl = {**p, **p.get("right", {})}  # asymmetry goes on the character's right eye (viewer left)
    pl.pop("right", None)
    draw_eye(c, 70, 78, pl, look_dx, blink, side=-1)
    pr = dict(p)
    pr.pop("right", None)
    draw_eye(c, 180, 78, pr, look_dx, blink, side=+1)
    return c


# ============================================================ MOUTH =========
# viseme -> (width, height, teeth_top, teeth_bottom, tongue, shape)
VISEMES = {
    "a_e":       dict(w=76, h=34, teeth=True, tongue=False),
    "d_j_ch":    dict(w=64, h=20, teeth=True, tongue=False),
    "f":         dict(w=66, h=16, teeth=True, tongue=False, lower_lip_in=True),
    "l":         dict(w=60, h=30, teeth=False, tongue=True),
    "m_b_close": dict(w=70, h=0, teeth=False, tongue=False),
    "o_big":     dict(w=50, h=44, teeth=False, tongue=False, round=True),
    "oh":        dict(w=42, h=32, teeth=False, tongue=False, round=True),
    "o_small":   dict(w=28, h=22, teeth=False, tongue=False, round=True),
    "th":        dict(w=62, h=18, teeth=True, tongue=True),
    "trans":     dict(w=50, h=12, teeth=False, tongue=False),
}


def draw_mouth(viseme, mood):
    v = VISEMES[viseme]
    c = Canvas(MOUTH_W, MOUTH_H)
    cx, cy = MOUTH_W / 2, 26
    curl = 9 if mood == "happy" else -8  # corner lift (+ up)
    w, h = v["w"], v["h"]
    if h == 0:  # closed
        pts = bezier((cx - w / 2, cy - curl), (cx - w / 4, cy + curl * 0.8), (cx + w / 4, cy + curl * 0.8), (cx + w / 2, cy - curl))
        c.line(pts, fill=LIP, width=10)
        c.line(pts, fill=INK, width=5)
        return c
    if v.get("round"):
        c.ellipse(cx, cy + (2 if mood == "sad" else -2), w / 2, h / 2, MOUTH_IN, INK, OUTLINE)
        c.ellipse(cx, cy + (2 if mood == "sad" else -2), w / 2 - 4, h / 2 - 4, None, LIP, 4)
        return c
    # open mouth: upper lip line + lower lip curve, corners lifted or dropped
    l, r = (cx - w / 2, cy - curl), (cx + w / 2, cy - curl)
    top = bezier(l, (cx - w / 4, cy - curl * 0.2 - 2), (cx + w / 4, cy - curl * 0.2 - 2), r)
    bot = bezier(r, (cx + w / 4, cy + h - curl * 0.3), (cx - w / 4, cy + h - curl * 0.3), l)
    shape = top + bot
    c.poly(shape, MOUTH_IN, INK, OUTLINE)
    if v.get("teeth"):
        tw = w * 0.42
        c.poly([(cx - tw, cy - curl * 0.4 + 2), (cx + tw, cy - curl * 0.4 + 2),
                (cx + tw * 0.95, cy - curl * 0.4 + 9), (cx - tw * 0.95, cy - curl * 0.4 + 9)], WHITE, None)
    if v.get("tongue"):
        c.ellipse(cx, cy + h * 0.65, w * 0.28, h * 0.32, TONGUE, None)
    if v.get("lower_lip_in"):
        c.line([(cx - w / 2, cy + h - 2), (cx, cy + h + 3), (cx + w / 2, cy + h - 2)], fill=LIP, width=7)
    return c


# ============================================================ BODY ==========
SHOULDER_R, SHOULDER_L = (300, 380), (500, 380)  # character's right = viewer left (x<400)
L1, L2 = 175, 165  # upper arm, forearm
REST_R, REST_L = (270, 690), (530, 690)


def ik_elbow(s, h, bend):
    """Two-link IK; bend=+1 puts the elbow on the +x side of the shoulder->hand line."""
    dx, dy = h[0] - s[0], h[1] - s[1]
    d = max(1e-6, min(math.hypot(dx, dy), L1 + L2 - 1))
    a = (L1 * L1 - L2 * L2 + d * d) / (2 * d)
    hh = math.sqrt(max(0.0, L1 * L1 - a * a))
    mx, my = s[0] + a * dx / d, s[1] + a * dy / d
    nx, ny = -dy / d, dx / d  # unit normal
    return (mx + bend * hh * nx, my + bend * hh * ny)


def draw_hand(c, h, kind, angle=None):
    r = 24
    c.ellipse(h[0], h[1], r, r, SKIN)
    if kind == "open":
        for i in range(4):
            a = math.radians((angle if angle is not None else -90) + (i - 1.5) * 24)
            fx, fy = h[0] + math.cos(a) * (r + 10), h[1] + math.sin(a) * (r + 10)
            c.thick_segment(h, (fx, fy), 12, SKIN, INK, 3)
    elif kind == "point":
        a = math.radians(angle if angle is not None else -90)
        fx, fy = h[0] + math.cos(a) * (r + 24), h[1] + math.sin(a) * (r + 24)
        c.thick_segment(h, (fx, fy), 14, SKIN, INK, 3)
    elif kind == "thumb":
        c.thick_segment(h, (h[0], h[1] - r - 20), 15, SKIN, INK, 3)
    elif kind == "flat":
        a = math.radians(angle if angle is not None else 0)
        fx, fy = h[0] + math.cos(a) * (r + 22), h[1] + math.sin(a) * (r + 22)
        c.thick_segment(h, (fx, fy), 30, SKIN, INK, 3)
    c.ellipse(h[0], h[1], r, r, SKIN)  # redraw palm over finger roots


def draw_arm(c, shoulder, hand, bend, kind="fist", angle=None):
    if bend is None:  # auto: elbow away from the body centre line; near-tie -> lower elbow
        cands = [ik_elbow(shoulder, hand, b) for b in (+1, -1)]
        out = [abs(e[0] - BODY_W / 2) for e in cands]
        e = cands[0] if out[0] > out[1] + 15 else cands[1] if out[1] > out[0] + 15 else max(cands, key=lambda q: q[1])
    else:
        e = ik_elbow(shoulder, hand, bend)
    c.thick_segment(shoulder, e, 46, KAMEEZ)
    c.thick_segment(e, hand, 42, KAMEEZ)
    c.ellipse(e[0], e[1], 23, 23, KAMEEZ, None)
    draw_hand(c, hand, kind, angle)


def draw_torso(c, slump=0):
    y0 = 340 + slump
    # shalwar (legs) and shoes first
    c.poly([(300, 700), (500, 700), (520, 1010), (415, 1010), (400, 830), (385, 1010), (280, 1010)], SHALWAR)
    c.ellipse(332, 1020, 58, 22, SHOE)
    c.ellipse(468, 1020, 58, 22, SHOE)
    # kameez
    hem = bezier((262, 760), (330, 785), (470, 785), (538, 760))
    body = [(300, y0), (500, y0), (540, y0 + 40), (538, 760)] + hem[::-1][1:-1] + [(262, 760), (260, y0 + 40)]
    c.poly(body, KAMEEZ)
    c.poly([(262, 760), (538, 760)] + hem[::-1], KAMEEZ_SHADE, None)
    c.ellipse(300, y0 + 22, 40, 26, KAMEEZ)
    c.ellipse(500, y0 + 22, 40, 26, KAMEEZ)
    # collar (round neck) — the head's neck lands here
    c.ellipse(400, y0 + 8, 44, 18, SKIN_SHADE)
    # dupatta drape across the chest from the left shoulder to the right hip
    drape = [(505, y0 - 6), (540, y0 + 40), (420, 720), (330, 720), (455, y0 + 10)]
    c.poly(drape, DUPATTA)
    c.line([(455, y0 + 10), (330, 720)], fill=DUPATTA_SHADE, width=10)


# pose name -> right hand, left hand, right bend, left bend, right kind, left kind, extras
POSES = {
    "standing":     dict(rh=REST_R, lh=REST_L),
    "explain":      dict(lh=(640, 480), lk="open", la=-20),
    "answer":       dict(lh=(575, 320), lk="point", la=-90),
    "question":     dict(rh=(165, 480), lh=(635, 480), rk="open", lk="open", ra=-160, la=-20),
    "thinking":     dict(lh=(452, 372), lk="fist"),
    "idea":         dict(lh=(605, 205), lk="point", la=-90, bulb=(605, 120)),
    "hi":           dict(lh=(645, 250), lk="open", la=-90),
    "technical":    dict(rh=(340, 585), lh=(460, 585), tablet=(400, 560)),
    "this":         dict(lh=(620, 600), lk="point", la=40),
    "that":         dict(lh=(690, 400), lk="point", la=0),
    "you":          dict(lh=(600, 470), lk="point", la=20),
    "i":            dict(rh=(400, 470), rk="flat", ra=0),
    "me":           dict(rh=(400, 470), rk="flat", ra=0),
    "winner":       dict(rh=(200, 190), lh=(600, 190)),
    "joy":          dict(rh=(200, 190), lh=(600, 190), rk="open", lk="open", ra=-90, la=-90),
    "jumping":      dict(rh=(190, 210), lh=(610, 210), rk="open", lk="open", ra=-90, la=-90),
    "achieve":      dict(lh=(600, 190)),
    "feeling_down": dict(rh=(300, 700), lh=(500, 700), slump=10, head_dy=12),
    "confuse":      dict(rh=(170, 480), lh=(560, 330), rk="open", ra=-160),
    "not_me":       dict(rh=(200, 385), lh=(600, 385), rk="open", lk="open", ra=-90, la=-90),
    "come":         dict(lh=(600, 420), lk="open", la=-140),
    "chilling":     dict(rh=(470, 520), lh=(330, 520)),
    "crazy":        dict(rh=(150, 250), lh=(650, 300), rk="open", lk="open", ra=-120, la=-60),
    "dancing":      dict(rh=(170, 250), lh=(620, 600), rk="open", lk="open", ra=-90, la=30),
    "kung_fu":      dict(rh=(330, 420), lh=(690, 380), lk="flat", la=0),
    "love":         dict(rh=(378, 480), lh=(422, 480)),
    "meditation":   dict(rh=(378, 640), lh=(422, 640)),
    "praying":      dict(rh=(386, 470), lh=(414, 470)),
    "model":        dict(lh=(545, 660)),
    "paper":        dict(rh=(335, 565), lh=(465, 565), paper=(400, 560)),
    "running":      dict(rh=(230, 480), lh=(560, 440)),
    "search":       dict(lh=(545, 335), lb=-1, lk="flat", la=180),
    "shy":          dict(rh=(385, 700), lh=(415, 700), head_dy=8),
    "singing":      dict(lh=(560, 365), mic=True),
    "sneaky":       dict(rh=(370, 450), lh=(430, 450)),
    "yeah":         dict(lh=(600, 400), lk="thumb"),
    "idk":          dict(rh=(165, 480), lh=(635, 480), rk="open", lk="open", ra=-160, la=-20),
    "what":         dict(rh=(180, 470), lh=(620, 470), rk="open", lk="open", ra=-160, la=-20),
    "why":          dict(rh=(170, 490), lh=(630, 490), rk="open", lk="open", ra=-160, la=-20),
}


def draw_body(pose):
    p = POSES[pose]
    c = Canvas(BODY_W, BODY_H)
    slump = p.get("slump", 0)
    rh, lh = p.get("rh", REST_R), p.get("lh", REST_L)
    # arms behind the torso for crossed/rest poses? keep arms in front except rest
    draw_torso(c, slump)
    if "paper" in p:
        x, y = p["paper"]
        c.poly([(x - 85, y - 105), (x + 85, y - 95), (x + 80, y + 100), (x - 80, y + 90)], WHITE)
        for i in range(5):
            c.line([(x - 55, y - 60 + i * 30), (x + 55, y - 58 + i * 30)], fill=(150, 150, 150, 255), width=4)
    if "tablet" in p:
        x, y = p["tablet"]
        c.poly([(x - 95, y - 70), (x + 95, y - 70), (x + 95, y + 70), (x - 95, y + 70)], (60, 60, 70, 255))
        c.poly([(x - 82, y - 58), (x + 82, y - 58), (x + 82, y + 58), (x - 82, y + 58)], (120, 200, 230, 255), None)
        c.line([(x - 60, y - 25), (x + 20, y - 25)], fill=WHITE, width=6)
        c.line([(x - 60, y + 5), (x + 50, y + 5)], fill=WHITE, width=6)
    if "bulb" in p:
        x, y = p["bulb"]
        c.ellipse(x, y, 34, 34, (255, 236, 120, 255))
        c.poly([(x - 14, y + 30), (x + 14, y + 30), (x + 12, y + 50), (x - 12, y + 50)], (170, 170, 170, 255))
        for a in range(0, 360, 60):
            r = math.radians(a)
            c.line([(x + math.cos(r) * 46, y + math.sin(r) * 46), (x + math.cos(r) * 60, y + math.sin(r) * 60)],
                   fill=(255, 200, 60, 255), width=5)
    draw_arm(c, (SHOULDER_R[0], SHOULDER_R[1] + slump), rh, p.get("rb"), p.get("rk", "fist"), p.get("ra"))
    draw_arm(c, (SHOULDER_L[0], SHOULDER_L[1] + slump), lh, p.get("lb"), p.get("lk", "fist"), p.get("la"))
    if p.get("mic"):
        c.thick_segment(lh, (lh[0] + 5, lh[1] - 70), 16, (60, 60, 60, 255))
        c.ellipse(lh[0] + 6, lh[1] - 80, 22, 22, (90, 90, 100, 255))
    return c, p.get("head_dy", 0)


# ============================================================ MAIN ==========
def happy_mouth_set():
    return {"happy", "content", "sarcasm", "crazy", "evil_laugh", "lust", "silly"}


def build(out_root, char1_root):
    meta = {"eyes": {}, "mouth": {}, "body": {}, "background": {}}
    # heads
    for d in "LMR":
        draw_head(d).save(os.path.join(out_root, "head", d, f"head_{d}.png"))
    # eyes: 14 emotions x {"", "_2"} x (L,M,R) + blink folder (02,03,04 + L,M,R copies)
    for name in emotions.values():
        for folder in (name, name + "_2"):
            base = os.path.join(out_root, "eyes", folder)
            blink_dir = os.path.join(base, folder + "_blink")
            for look in "LMR":
                img = draw_eyes(folder, look)
                img.save(os.path.join(base, f"{folder}_{look}.png"))
                img.save(os.path.join(blink_dir, f"{folder}_{look}.png"))
            draw_eyes(folder, "M", "half").save(os.path.join(blink_dir, "02.png"))
            draw_eyes(folder, "M", "closed").save(os.path.join(blink_dir, "03.png"))
            draw_eyes(folder, "M", "half").save(os.path.join(blink_dir, "04.png"))
            meta["eyes"][folder] = {"position": list(EYES_POS), "size": [EYES_W, EYES_H]}
    # mouths
    for vis in VISEMES:
        for mood, suf in (("happy", "h"), ("sad", "s")):
            key = f"{vis}_{suf}"
            draw_mouth(vis, mood).save(os.path.join(out_root, "mouth", mood, f"{key}.png"))
            meta["mouth"][key] = {"position": list(MOUTH_POS), "size": [MOUTH_W, MOUTH_H]}
    # bodies: one PNG per distinct action, file stem == action so metadata is per pose
    for action in sorted(set(body_actions.values())):
        img, head_dy = draw_body(action)
        img.save(os.path.join(out_root, "body", action, f"{action}.png"))
        meta["body"][action] = {
            "position": [HEAD_ON_BODY[0], HEAD_ON_BODY[1] + head_dy],
            "size": [HEAD_W, HEAD_H],
            "neck": [NECK[0], NECK[1] + head_dy],
        }
    # backgrounds: reuse character_1 plates, renamed so file stem == folder == metadata key
    names = {m["name"] for m in screen_mode.values()} | {"gardan"}
    for name in sorted(names):
        src_dir = os.path.join(char1_root, "background", "garden" if name == "gardan" else name)
        srcs = [f for f in os.listdir(src_dir) if f.endswith(".png")]
        dst = os.path.join(out_root, "background", name, f"{name}.png")
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(os.path.join(src_dir, srcs[0]), dst)
        meta["background"][name] = {
            "size": [BODY_W, BODY_H], "position": list(BODY_ON_BG),
            "mirror": False, "addition": True, "zoom_point": list(ZOOM_POINT),
        }
    return meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="images/characters/character_2")
    ap.add_argument("--char1", default="images/characters/character_1")
    ap.add_argument("--metadata", default="images/metadata/metadata.json")
    ap.add_argument("--no-metadata", action="store_true")
    a = ap.parse_args()
    meta = build(a.out, a.char1)
    if not a.no_metadata:
        with open(a.metadata) as f:
            all_meta = json.load(f)
        all_meta[os.path.basename(a.out.rstrip("/"))] = meta
        with open(a.metadata, "w") as f:
            json.dump(all_meta, f, indent=4)
    n = sum(len(fs) for _, _, fs in os.walk(a.out))
    print(f"built {n} files under {a.out}; metadata {'skipped' if a.no_metadata else 'updated'}")


if __name__ == "__main__":
    main()
