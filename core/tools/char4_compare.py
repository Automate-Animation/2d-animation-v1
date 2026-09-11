#!/usr/bin/env python3
"""Build side-by-side character_1 vs character_4 comparison sheets for the harsh QA pass
(SKILL.md step H). Writes build/qa/character_4/compare_visemes.png and compare_emotions.png.
Run from core/: ../.venv/bin/python tools/char4_compare.py
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from image_manager.CharacterManager import CharacterManager  # noqa: E402
from utils.constants import emotions  # noqa: E402

BASE = "images/characters"
META = "images/metadata/metadata.json"
VISEMES = ["a_e", "d_j_ch", "f", "l", "m_b_close", "o_big", "o_small", "oh", "th", "trans"]
HAPPY = {"happy", "content", "sarcasm", "crazy", "evil_laugh", "lust", "silly"}


def tile_pair(im1, im2, label, tw=260, th=260):
    pad = 6
    canvas = Image.new("RGB", (tw * 2 + pad * 3, th + 24), (30, 30, 30))
    d = ImageDraw.Draw(canvas)
    canvas.paste(im1.convert("RGB").resize((tw, th)), (pad, 24))
    canvas.paste(im2.convert("RGB").resize((tw, th)), (pad * 2 + tw, 24))
    d.text((pad, 4), f"{label}  (L=character_1, R=character_4)", fill=(255, 255, 0), font=ImageFont.load_default())
    return canvas


def grid(tiles, path, cols=4):
    if not tiles:
        return
    w, h = tiles[0].size
    rows = (len(tiles) + cols - 1) // cols
    im = Image.new("RGB", (cols * w, rows * h), (10, 10, 10))
    for i, t in enumerate(tiles):
        im.paste(t, ((i % cols) * w, (i // cols) * h))
    im.save(path)
    print("wrote", path)


def crop_head_zoom(mgr, char, folder, mood, vis_or_folder_label, headzoom_fn):
    img, _ = mgr.get_character(char, folder, "explain" if char == "character_1" else "explain",
                                "M", f"{folder}_M", "white", mood, vis_or_folder_label, 0)
    return headzoom_fn(char, img)


def main():
    mgr = CharacterManager(BASE, META)
    meta = json.load(open(META))

    def headzoom(char, im):
        m = meta[char]
        # character_1's body metadata is keyed by FILE STEM (e.g. "body15"), not action name --
        # character_4's is keyed by the action name itself. Resolve to whichever file is
        # actually on disk for the "explain" folder (every tile below composes with that body).
        explain_dir = f"images/characters/{char}/body/explain"
        bfile = sorted(os.listdir(explain_dir))[0]
        stem = os.path.splitext(bfile)[0]
        b0 = m["body"][stem]
        white_dir = f"images/characters/{char}/background/white"
        wfile = sorted(os.listdir(white_dir))[0]
        wstem = os.path.splitext(wfile)[0]
        bg0 = m["background"][wstem]
        # adding_image resizes the WHOLE body canvas (its own on-disk size, which for
        # character_4 varies per pose -- NOT a shared fixed canvas like character_1's 800x1080)
        # to bg0["size"] before mirroring, so the head box must be scaled by that per-axis ratio
        # before mirroring -- a fixed-pivot formula (assuming body canvas width == bg size width)
        # is what silently produced an empty crop for character_4's differently-sized canvases.
        body_w, body_h = Image.open(f"{explain_dir}/{bfile}").size
        sx, sy = bg0["size"][0] / body_w, bg0["size"][1] / body_h
        hx_raw, hy_raw = b0["position"]
        hw_raw, hh_raw = b0["size"]
        hw, hh = hw_raw * sx, hh_raw * sy
        hx_scaled = hx_raw * sx
        hx = bg0["size"][0] - hx_scaled - hw  # mirrored within the resized bg box
        hy = hy_raw * sy
        x0 = bg0["position"][0] + hx - 40
        y0 = max(0, bg0["position"][1] + hy - 30)
        return im.crop((int(x0), int(y0), int(x0 + hw + 80), int(y0 + hh + 60)))

    # visemes
    tiles = []
    for vis in VISEMES:
        mood = "happy"
        suf = "h"
        key = f"{vis}_{suf}"
        im1, _ = mgr.get_character("character_1", "happy", "explain", "M", "happy_M", "white", mood, key, 0)
        im4, _ = mgr.get_character("character_4", "happy", "explain", "M", "happy_M", "white", mood, key, 0)
        tiles.append(tile_pair(headzoom("character_1", im1), headzoom("character_4", im4), f"viseme={vis} ({mood})"))
    grid(tiles, "build/qa/character_4/compare_visemes.png", cols=4)

    # emotions
    tiles = []
    for e in emotions.values():
        mood = "happy" if e in HAPPY else "sad"
        suf = "h" if mood == "happy" else "s"
        im1, _ = mgr.get_character("character_1", e, "explain", "M", f"{e}_M", "white", mood, f"a_e_{suf}", 0)
        im4, _ = mgr.get_character("character_4", e, "explain", "M", f"{e}_M", "white", mood, f"a_e_{suf}", 0)
        tiles.append(tile_pair(headzoom("character_1", im1), headzoom("character_4", im4), f"emotion={e}"))
    # blink frames (happy)
    for b in ("happy_M", "02", "03", "04"):
        im1, _ = mgr.get_character("character_1", "happy", "explain", "M", b, "white", "happy", "a_e_h", 0, blink=True)
        im4, _ = mgr.get_character("character_4", "happy", "explain", "M", b, "white", "happy", "a_e_h", 0, blink=True)
        tiles.append(tile_pair(headzoom("character_1", im1), headzoom("character_4", im4), f"blink={b}"))
    grid(tiles, "build/qa/character_4/compare_emotions.png", cols=4)

    # bodies
    from utils.constants import body_actions
    tiles = []
    for a in sorted(set(body_actions.values())):
        im1, _ = mgr.get_character("character_1", "happy", a, "M", "happy_M", "classroom", "happy", "m_b_close_h", 0)
        im4, _ = mgr.get_character("character_4", "happy", a, "M", "happy_M", "classroom", "happy", "m_b_close_h", 0)
        tiles.append(tile_pair(im1, im4, f"body={a}", tw=220, th=300))
    grid(tiles, "build/qa/character_4/compare_bodies.png", cols=4)


if __name__ == "__main__":
    main()
