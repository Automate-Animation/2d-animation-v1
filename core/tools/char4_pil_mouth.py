#!/usr/bin/env python3
"""Route-B PIL fallback for a single mouth viseme, used only if Gemini returns a dirty
sticker (skin/nose included) twice for that viseme. Draws a simple isolated mouth shape in
the reference character's lip/teeth colours. Writes directly into build/char4/src/mouth_<v>_<s>.png
(pre-chroma-key RGBA, so build_character_4.py's tight_crop can use it as-is -- skip key_green for
these by saving with real alpha already).
Usage: ../.venv/bin/python tools/char4_pil_mouth.py <viseme> <h|s>
"""
import sys

from PIL import Image, ImageDraw

LIP = (139, 40, 40, 255)      # warm dark red-brown, close to reference lip tone
LIP_DARK = (90, 20, 20, 255)
TEETH = (255, 255, 255, 255)
TONGUE = (200, 90, 90, 255)

SHAPES = {
    "a_e": "wide_open", "d_j_ch": "parted", "f": "f_shape", "l": "tongue_l",
    "m_b_close": "closed", "o_big": "round_big", "o_small": "round_small",
    "oh": "oval", "th": "tongue_th", "trans": "relaxed",
}


def draw(shape, sad=False):
    W, H = 240, 160
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, cy = W // 2, H // 2
    droop = 10 if sad else 0
    if shape == "closed":
        d.line([(cx - 70, cy + droop), (cx - 20, cy + 6 + droop), (cx + 20, cy - 4 + droop), (cx + 70, cy + droop)],
               fill=LIP_DARK, width=10, joint="curve")
    elif shape in ("round_big", "round_small", "oval"):
        r = {"round_big": 55, "round_small": 34, "oval": 40}[shape]
        rh = r if shape != "oval" else int(r * 1.3)
        d.ellipse([cx - r, cy - rh + droop, cx + r, cy + rh + droop], fill=TEETH, outline=LIP, width=8)
    elif shape == "wide_open":
        d.polygon([(cx - 90, cy - 10 + droop), (cx + 90, cy - 10 + droop), (cx + 60, cy + 40 + droop),
                   (cx - 60, cy + 40 + droop)], fill=LIP)
        d.rectangle([cx - 70, cy - 8 + droop, cx + 70, cy + 8 + droop], fill=TEETH)
    elif shape == "f_shape":
        d.rectangle([cx - 75, cy - 5 + droop, cx + 75, cy + 5 + droop], fill=TEETH)
        d.line([(cx - 80, cy + 20 + droop), (cx + 80, cy + 20 + droop)], fill=LIP, width=14)
    elif shape in ("tongue_l", "tongue_th"):
        d.polygon([(cx - 80, cy - 5 + droop), (cx + 80, cy - 5 + droop), (cx + 55, cy + 35 + droop),
                   (cx - 55, cy + 35 + droop)], fill=(30, 10, 10, 255))
        d.ellipse([cx - 25, cy - 5 + droop, cx + 25, cy + 25 + droop], fill=TONGUE)
    else:  # parted / relaxed
        d.polygon([(cx - 85, cy + droop), (cx + 85, cy + droop), (cx + 60, cy + 22 + droop),
                   (cx - 60, cy + 22 + droop)], fill=LIP)
    return im


def main():
    vis, suf = sys.argv[1], sys.argv[2]
    shape = SHAPES[vis]
    im = draw(shape, sad=(suf == "s"))
    out = f"build/char4/src/mouth_{vis}_{suf}_PILFALLBACK.png"
    im.save(out)
    print("wrote", out, "-- rename to mouth_%s_%s.png to use, and it's pre-keyed (real alpha already)" % (vis, suf))


if __name__ == "__main__":
    main()
