#!/usr/bin/env python3
"""QA gate for a synctoon character. Run from core/:  python tools/character_qa.py character_2
Checks every file constants.py implies, boxes inside parent canvases, eyes above mouth, head on neck (metadata.body[*].neck
or first real opaque row); renders all emotions x head dirs + all bodies via CharacterManager to build/qa/<char>/. Exit 1 on FAIL."""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from image_manager.CharacterManager import CharacterManager  # noqa: E402
from utils.constants import body_actions, emotions, screen_mode  # noqa: E402

BASE = "images/characters"
META = "images/metadata/metadata.json"
VISEMES = ["a_e", "d_j_ch", "f", "l", "m_b_close", "o_big", "o_small", "oh", "th", "trans"]
HAPPY = {"happy", "content", "sarcasm", "crazy", "evil_laugh", "lust", "silly"}
errors = []

def check(cond, msg):
    errors.extend([] if cond else [msg])

def inside(box, size):
    return box[0] >= 0 and box[1] >= 0 and box[0] + box[2] <= size[0] and box[1] + box[3] <= size[1]

def first_png(folder):
    fs = sorted(f for f in os.listdir(folder) if f.endswith(".png")) if os.path.isdir(folder) else []
    return os.path.join(folder, fs[0]) if fs else None

def structure_and_geometry(char, meta):
    root = os.path.join(BASE, char)
    m = meta.get(char)
    if not check(m is not None, f"{char} missing from {META}") and m is None:
        return
    head = first_png(os.path.join(root, "head", "M"))
    check(head is not None, "head/M has no png")
    hsize = Image.open(head).size if head else (0, 0)
    for d in "LMR":
        p = first_png(os.path.join(root, "head", d))
        check(p is not None, f"head/{d} missing")
        check(p is None or Image.open(p).size == hsize, f"head/{d} size differs from head/M")
    eye_boxes, mouth_boxes = [], []
    for e in emotions.values():
        for folder in (e, e + "_2"):
            files = [f"{folder}_{k}.png" for k in "LMR"] + [f"{folder}_blink/{n}.png" for n in ("02", "03", "04", f"{folder}_L", f"{folder}_M", f"{folder}_R")]
            for f in files:
                check(os.path.exists(f"{root}/eyes/{folder}/{f}"), f"eyes/{folder}/{f} missing")
            em = m["eyes"].get(folder)
            check(em is not None, f"metadata.eyes[{folder}] missing")
            if em:
                box = (*em["position"], *em["size"])
                check(inside(box, hsize), f"eyes[{folder}] box {box} outside head {hsize}")
                eye_boxes.append(box)
    for v in VISEMES:
        for mood, suf in (("happy", "h"), ("sad", "s")):
            key = f"{v}_{suf}"
            check(os.path.exists(f"{root}/mouth/{mood}/{key}.png"), f"mouth/{mood}/{key}.png missing")
            mm = m["mouth"].get(key)
            check(mm is not None, f"metadata.mouth[{key}] missing")
            if mm:
                box = (*mm["position"], *mm["size"])
                check(inside(box, hsize), f"mouth[{key}] box {box} outside head {hsize}")
                mouth_boxes.append(box)
    if eye_boxes and mouth_boxes:
        eye_bottom = max(b[1] + b[3] for b in eye_boxes)
        mouth_top = min(b[1] for b in mouth_boxes)
        check(eye_bottom <= mouth_top, f"eye box bottom {eye_bottom} is below mouth top {mouth_top}")
    for action in sorted(set(body_actions.values())):
        p = first_png(os.path.join(root, "body", action))
        stem = p and os.path.splitext(os.path.basename(p))[0]
        bm = p and m["body"].get(stem)
        check(bool(bm), f"body/{action}: png or metadata.body[{stem}] missing")
        if not bm:
            continue
        body = Image.open(p)
        box = (*bm["position"], *bm["size"])
        check(inside(box, body.size), f"body[{stem}] head box {box} outside body canvas {body.size}")
        neck = bm.get("neck")
        if neck is None:  # derive: topmost opaque row, centre of that row
            a = body.getchannel("A")
            rows = ((y, [x for x in range(body.size[0]) if a.getpixel((x, y)) > 128]) for y in range(body.size[1]))
            y, row = next((y, r) for y, r in rows if len(r) >= 10)  # first row with a real silhouette
            neck = (sum(row) / len(row), y)
        hx, hy = box[0] + box[2] / 2, box[1] + box[3]
        check(abs(hx - neck[0]) <= box[2] * 0.15 and abs(hy - neck[1]) <= box[3] * 0.2,
              f"body[{stem}] head bottom-centre ({hx:.0f},{hy:.0f}) not on neck {tuple(round(v) for v in neck)}")
    for name in {s["name"] for s in screen_mode.values()} | {"gardan"}:
        p = first_png(os.path.join(root, "background", name))
        gm = p and m["background"].get(os.path.splitext(os.path.basename(p))[0])
        check(bool(gm), f"background/{name}: png or metadata key missing")
        if gm:
            check(inside((*gm["position"], *gm["size"]), Image.open(p).size), f"background[{name}] body box outside canvas")

def sheet(tiles, path, cols=5, tw=384, th=216):
    rows = (len(tiles) + cols - 1) // cols
    im = Image.new("RGB", (cols * tw, rows * (th + 22)), (40, 40, 40))
    d = ImageDraw.Draw(im)
    for i, (label, img) in enumerate(tiles):
        x, y = (i % cols) * tw, (i // cols) * (th + 22)
        im.paste(img.convert("RGB").resize((tw, th)), (x, y + 22))
        d.text((x + 4, y + 4), label, fill=(255, 255, 0), font=ImageFont.load_default())
    im.save(path)

def render_sheets(char, out):
    mgr = CharacterManager(BASE, META)
    os.makedirs(out, exist_ok=True)
    tiles = []
    for i, e in enumerate(emotions.values()):
        for folder in (e, e + "_2"):
            mood = "happy" if e in HAPPY else "sad"
            for d in "LMR":
                vis = VISEMES[(i + "LMR".index(d)) % len(VISEMES)]
                img, _ = mgr.get_character(char, folder, "explain", d, f"{folder}_{d}", "white", mood, f"{vis}_{mood[0]}", 0)
                tiles.append((f"{folder} head={d} {vis}", img))
    for n in range(0, len(tiles), 20):
        sheet(tiles[n:n + 20], f"{out}/faces_{n // 20 + 1:02d}.png")
    m = json.load(open(META))[char]
    b0 = next(iter(m["body"].values()))
    bg0 = next(iter(m["background"].values()))
    hx, hy, hw, hh = b0["position"][0], b0["position"][1], b0["size"][0], b0["size"][1]
    hx = bg0["size"][0] - hx - hw  # body is mirrored onto the background
    x0, y0 = bg0["position"][0] + hx - 40, max(0, bg0["position"][1] + hy - 30)
    zoom = [(lab, im.crop((x0, y0, x0 + hw + 80, y0 + hh + 60))) for lab, im in tiles]
    for n in range(0, len(zoom), 20):
        sheet(zoom[n:n + 20], f"{out}/faces_zoom_{n // 20 + 1:02d}.png", cols=5, tw=330, th=270)
    tiles = []
    for a in sorted(set(body_actions.values())):
        img, _ = mgr.get_character(char, "happy", a, "M", "happy_M", "classroom", "happy", "m_b_close_h", 0)
        tiles.append((a, img))
    for n in range(0, len(tiles), 20):
        sheet(tiles[n:n + 20], f"{out}/bodies_{n // 20 + 1:02d}.png")
    blink = []
    for b in ("happy_M", "02", "03", "04"):
        img, _ = mgr.get_character(char, "happy", "standing", "M", b, "white", "happy", "a_e_h", 2, blink=True)
        blink.append((f"blink {b} zoom2", img))
    sheet(blink, f"{out}/blink_zoom.png", cols=4)

def main():
    char = sys.argv[1] if len(sys.argv) > 1 else "character_2"
    meta = json.load(open(META))
    structure_and_geometry(char, meta)
    try:
        render_sheets(char, f"build/qa/{char}")
    except Exception as ex:  # noqa: BLE001 -- a missing file/key surfaces here as a FAIL, not a crash
        errors.append(f"compose failed: {ex!r}")
    print("\n".join("FAIL " + e for e in errors) + f"\n{char}: {len(errors)} problems; images in build/qa/{char}/")
    sys.exit(1 if errors else 0)

if __name__ == "__main__":
    main()
