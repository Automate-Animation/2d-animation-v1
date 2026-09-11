#!/usr/bin/env python3
"""Build character_3 ("Ustani") from Gemini-generated sources in build/char3/src/ + plate.png.

Method: plate + masked edits, FIXED crop boxes (see docs/CHARACTER_3_NOTES.md).
Every source image is an edit of the SAME plate/context crop, so they all share one coordinate
space. head/eyes/mouth all derive from the same CONTEXT crop box on the plate -> pasting head
back onto a body (which is the plate with the head region blanked) needs no re-alignment: it is
literally the same box. Eye/mouth boxes are found ONCE (on the neutral/happy reference) and reused
for every emotion/viseme since the edits preserve framing.

Run from core/:  ../.venv/bin/python tools/build_character_3.py [--no-metadata]
Re-runnable: pure post-processing of build/char3/{plate.png,src/*}; no network calls.
"""
import argparse
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.char3_lib import key_green, bbox, dark_blobs, row_widths  # noqa: E402
from utils.constants import body_actions, emotions, screen_mode  # noqa: E402

BUILD = "build/char3"
SRC = f"{BUILD}/src"
OUT = "images/characters/character_3"
CHAR1 = "images/characters/character_1"

CONTEXT = (236, 60, 616, 560)  # plate crop used as the face-edit context; also the body head-slot
CONTEXT_W, CONTEXT_H = CONTEXT[2] - CONTEXT[0], CONTEXT[3] - CONTEXT[1]  # 380x500: on-body paste size
# Gemini image-edit always returns a fixed default canvas for a cropped (non-full-frame) input,
# regardless of the input's own size -- verified: every eyes_*/mouth_*/head_L/R edit of context_M
# (380x500) came back 896x1152. head_M (cropped straight from the plate, not an edit) must be
# resized up to match so every head/eyes/mouth layer shares one canvas (and one set of boxes).
HEAD_W, HEAD_H = 896, 1152

# character_2-style eye/mouth folder->file naming
VISEMES = ["a_e", "d_j_ch", "f", "l", "m_b_close", "o_big", "o_small", "oh", "th", "trans"]
HAPPY_MOODS = {"happy", "content", "sarcasm", "crazy", "evil_laugh", "lust", "silly"}

# map every distinct body_action -> one of the 13 generated pose sources
POSE_MAP = {
    "achieve": "winner", "answer": "you", "explain": "explain", "me": "me", "not_me": "me",
    "question": "question", "technical": "technical", "why": "explain", "chilling": "standing",
    "come": "hi", "confuse": "question", "crazy": "winner", "dancing": "winner",
    "feeling_down": "feeling_down", "hi": "hi", "i": "me", "idea": "idea", "idk": "thinking",
    "joy": "joy", "jumping": "winner", "kung_fu": "kung_fu", "love": "hi", "meditation": "meditation",
    "model": "idea", "paper": "paper", "praying": "praying", "running": "joy", "search": "explain",
    "shy": "standing", "singing": "joy", "sneaky": "sneaky", "standing": "standing",
    "that": "question", "thinking": "thinking", "this": "you", "what": "question",
    "winner": "winner", "yeah": "winner", "you": "you",
}
# "standing" is not a generated pose (13 generated poses don't include a plain rest pose);
# use the plate itself (arms already relaxed) for the standing group.


def load_keyed(path):
    return key_green(Image.open(path).convert("RGB"))


def find_eye_mouth_boxes():
    """Fixed boxes in CONTEXT-crop pixel space, derived once from representative sources."""
    ref = load_keyed(f"{SRC}/eyes_happy.png")
    b = bbox(ref)  # whole head bbox in this 896x1152 image
    blobs = dark_blobs(ref, b, thr=80)
    # Irises are two roughly-circular blobs of a plausible size in the upper-middle of the face --
    # NOT simply "biggest dark blobs": hair/fringe/hood-shadow blobs are much bigger and dark too,
    # and picking those instead (both near the centre, i.e. missing BOTH iris x-positions) collapses
    # the eye box to a narrow strip over the nose bridge that misses most of each eye. Filter by a
    # plausible iris area range first, then also require roughly square (w~h) blobs.
    h_span = b[3] - b[1]
    face_area = (b[2] - b[0]) * h_span
    candidates = [t for t in blobs
                  if b[1] + 0.25 * h_span < t[1] < b[1] + 0.55 * h_span  # vertical eye band
                  and 0.003 * face_area < t[4] < 0.03 * face_area        # plausible iris area
                  and 0.6 < t[2] / max(t[3], 1) < 1.6]                  # roughly circular (w~h)
    irises = sorted(candidates, key=lambda t: -t[4])[:2]
    if len(irises) < 2:  # fallback: original heuristic, better than crashing
        upper = [t for t in blobs if t[1] < b[1] + h_span * 0.6]
        irises = sorted(upper, key=lambda t: -t[4])[:2]
    xs = [c[0] for c in irises]
    ys = [c[1] for c in irises]
    cy = sum(ys) / len(ys)
    half_w = (max(xs) - min(xs)) / 2 + 90  # generous margin for eyebrows + lash detail
    x0, x1 = min(xs) - 90, max(xs) + 90
    y0, y1 = cy - 85, cy + 80  # generous margin: must fully cover the open eye for every emotion
    # AND fully hide it when a closed/half-blink asset is pasted over the same box
    eye_box = (max(0, int(x0)), max(0, int(y0)), min(ref.width, int(x1)), min(ref.height, int(y1)))

    mref = load_keyed(f"{SRC}/mouth_m_b_close_h.png") if os.path.exists(f"{SRC}/mouth_m_b_close_h.png") else load_keyed(f"{SRC}/mouth_a_e_h.png")
    mb = bbox(mref)
    mouth_blobs = dark_blobs(mref, mb, thr=110)
    lower = [t for t in mouth_blobs if t[1] > eye_box[3]]
    mouth_c = max(lower, key=lambda t: t[4]) if lower else (mb[0] + (mb[2] - mb[0]) / 2, mb[1] + (mb[3] - mb[1]) * 0.75, 0, 0, 0)
    mx, my = mouth_c[0], mouth_c[1]
    mouth_box = (int(mx - 90), int(my - 45), int(mx + 90), int(my + 55))
    return eye_box, mouth_box


def cut_box(img, box):
    return img.crop(box)


def build_heads(out_root, meta):
    # head_M must live in the SAME output canvas as the eyes/mouth edits (896x1152), not a naive
    # crop+resize of the plate: Gemini's edit canvas for a cropped input is NOT a uniform rescale
    # of the crop (verified: a plate-crop+resize head landed ~13px off from the eyes_* face bbox,
    # enough for a closed-eyes paste to miss the head's own baked-in open eyes underneath and show
    # both at once). Since every eyes_*/mouth_*/head_L/R edit of context_M shares one canvas AND
    # its own baked eyes/mouth get fully overwritten by whatever gets pasted anyway, any one of
    # them is a safe head_M base -- eyes_happy.png IS the very reference find_eye_mouth_boxes()
    # used, so it aligns with the fixed boxes by construction.
    for d, srcfile in (("M", f"{SRC}/eyes_happy.png"), ("L", f"{SRC}/head_L.png"), ("R", f"{SRC}/head_R.png")):
        head = load_keyed(srcfile)
        if head.size != (HEAD_W, HEAD_H):
            head = head.resize((HEAD_W, HEAD_H))
        p = f"{out_root}/head/{d}/head_{d}.png"
        os.makedirs(os.path.dirname(p), exist_ok=True)
        head.save(p)


def build_eyes(out_root, meta, eye_box):
    ex0, ey0, ex1, ey1 = eye_box
    epos = (ex0, ey0)
    esize = (ex1 - ex0, ey1 - ey0)
    for name in emotions.values():
        for folder in (name, name + "_2"):
            base = os.path.join(out_root, "eyes", folder)
            blink_dir = os.path.join(base, folder + "_blink")
            os.makedirs(blink_dir, exist_ok=True)
            src = f"{SRC}/eyes_{name}.png"
            crop = cut_box(load_keyed(src), eye_box)
            half = cut_box(load_keyed(f"{SRC}/eyes__half.png"), eye_box)
            closed = cut_box(load_keyed(f"{SRC}/eyes__closed.png"), eye_box)
            for look in "LMR":
                crop.save(f"{base}/{folder}_{look}.png")
                crop.save(f"{blink_dir}/{folder}_{look}.png")
            half.save(f"{blink_dir}/02.png")
            closed.save(f"{blink_dir}/03.png")
            half.save(f"{blink_dir}/04.png")
            meta["eyes"][folder] = {"position": list(epos), "size": list(esize)}


def build_mouths(out_root, meta, mouth_box):
    mpos = (mouth_box[0], mouth_box[1])
    msize = (mouth_box[2] - mouth_box[0], mouth_box[3] - mouth_box[1])
    for vis in VISEMES:
        for mood, suf in (("happy", "h"), ("sad", "s")):
            key = f"{vis}_{suf}"
            src = f"{SRC}/mouth_{vis}_{suf}.png"
            if not os.path.exists(src):
                # fallback: closest available viseme of the same mood
                src = f"{SRC}/mouth_m_b_close_{suf}.png" if os.path.exists(f"{SRC}/mouth_m_b_close_{suf}.png") else f"{SRC}/mouth_a_e_{suf}.png"
            crop = cut_box(load_keyed(src), mouth_box)
            os.makedirs(f"{out_root}/mouth/{mood}", exist_ok=True)
            crop.save(f"{out_root}/mouth/{mood}/{key}.png")
            meta["mouth"][key] = {"position": list(mpos), "size": list(msize)}


def build_bodies(out_root, meta):
    # cut line: body_* sources are edits of the FULL plate (same 864x1184 coordinate space as
    # CONTEXT), so the collar sits right where the head crop box ends -- no detection needed,
    # just cut a little above the bottom of CONTEXT so a sliver of neck/collar stays on the body.
    cut_y = CONTEXT[3] - 15

    def to_body_layer(rgba):
        # Blank only the HEAD COLUMN above the collar (where the separate head layer will sit),
        # not the whole row -- poses with arms raised above the collar (winner, hi, idea...) have
        # real content up there that must stay on the body layer.
        arr = np.array(rgba)
        arr[:cut_y, CONTEXT[0]:CONTEXT[2], 3] = 0
        return Image.fromarray(arr, "RGBA")

    done = set()
    for action in sorted(set(body_actions.values())):
        pose = POSE_MAP.get(action, "standing")
        srcfile = f"{SRC}/body_{pose}.png" if pose != "standing" else f"{BUILD}/plate.png"
        if not os.path.exists(srcfile):
            srcfile = f"{BUILD}/plate.png"
        img = key_green(Image.open(srcfile).convert("RGB"))
        body = to_body_layer(img)
        d = f"{out_root}/body/{action}"
        os.makedirs(d, exist_ok=True)
        body.save(f"{d}/{action}.png")
        meta["body"][action] = {
            "position": [CONTEXT[0], CONTEXT[1]],
            "size": [CONTEXT_W, CONTEXT_H],
            "neck": [CONTEXT[0] + CONTEXT_W / 2, cut_y],
        }
        done.add(action)


def build_backgrounds(out_root, meta):
    plate = Image.open(f"{BUILD}/plate.png")
    bw, bh = plate.size
    BG_W, BG_H = 1920, 1080
    scale = min(BG_W * 0.42 / bw, BG_H * 0.95 / bh)
    dw, dh = int(bw * scale), int(bh * scale)
    bx = (BG_W - dw) // 2
    by = BG_H - dh
    names = {m["name"] for m in screen_mode.values()} | {"gardan"}
    for name in sorted(names):
        src_dir = os.path.join(CHAR1, "background", "garden" if name == "gardan" else name)
        if not os.path.isdir(src_dir):
            continue
        srcs = [f for f in os.listdir(src_dir) if f.endswith(".png")]
        if not srcs:
            continue
        dst = os.path.join(out_root, "background", name, f"{name}.png")
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(os.path.join(src_dir, srcs[0]), dst)
        meta["background"][name] = {
            "size": [dw, dh], "position": [bx, by],
            "mirror": False, "addition": True,
            "zoom_point": [bx + dw // 2, by + int(dh * 0.18)],
        }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--metadata", default="images/metadata/metadata.json")
    ap.add_argument("--no-metadata", action="store_true")
    a = ap.parse_args()
    meta = {"eyes": {}, "mouth": {}, "body": {}, "background": {}}
    eye_box, mouth_box = find_eye_mouth_boxes()
    print("eye_box", eye_box, "mouth_box", mouth_box)
    build_heads(a.out, meta)
    build_eyes(a.out, meta, eye_box)
    build_mouths(a.out, meta, mouth_box)
    build_bodies(a.out, meta)
    build_backgrounds(a.out, meta)
    if not a.no_metadata:
        all_meta = json.load(open(a.metadata))
        all_meta[os.path.basename(a.out.rstrip("/"))] = meta
        json.dump(all_meta, open(a.metadata, "w"), indent=4)
    n = sum(len(fs) for _, _, fs in os.walk(a.out))
    print(f"built {n} files under {a.out}; metadata {'skipped' if a.no_metadata else 'updated'}")


if __name__ == "__main__":
    main()
