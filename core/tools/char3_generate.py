#!/usr/bin/env python3
"""Generate every Gemini source image for character_3 into build/char3/src/. Re-runnable: skips files that exist.
Run from core/:  ../.venv/bin/python tools/char3_generate.py [--only heads|eyes|mouths|bodies] [--force name]
All face edits use the same CONTEXT crop of the plate (face + hood + shoulder tops, green bg) as the source image.
"""
import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.gemini_img import gen, calls  # noqa: E402

BUILD = "build/char3"
SRC = f"{BUILD}/src"
PLATE = f"{BUILD}/plate.png"
CONTEXT = (236, 60, 616, 560)  # plate crop given to face edits (380x500)

KEEP = ("Edit this flat cartoon illustration. Keep EVERYTHING exactly the same — same character, same size, same "
        "position in the frame, same framing, same flat colours, same thick dark outlines, same plain flat green "
        "background, no shadow, no text — ")

EYES = {
    "happy":      "smiling happy eyes, gently squinted with joy, relaxed slightly raised brows",
    "sad":        "sad eyes, drooping upper eyelids, brows angled upward at the inner ends",
    "angry":      "angry eyes, brows lowered and pulled together toward the nose, narrowed stern eyes",
    "bore":       "bored eyes, heavy half-closed lids covering the top half of the eyes, flat brows",
    "content":    "content calm eyes, softly half-lidded with a gentle satisfied look, relaxed brows",
    "glare":      "glaring eyes, narrowed intense stare, brows pressed down flat",
    "sarcasm":    "sceptical sarcastic eyes: one eyebrow raised high, the other lowered, eyes half-lidded",
    "worried":    "worried anxious eyes, wide open, brows raised and pulled together with inner ends up",
    "crazy":      "wild crazy eyes, both wide open, one eye bigger than the other, eyebrows uneven and jagged",
    "evil_laugh": "mischievous laughing eyes squeezed into narrow curved slits, brows sharply angled down toward the nose",
    "lust":       "dreamy admiring eyes, half-lidded with long lashes, brows softly raised",
    "shock":      "shocked eyes, very wide open and round, small irises, brows raised very high",
    "silly":      "silly playful cross-eyed look, irises pointing inward toward the nose, brows raised unevenly",
    "spoked":     "frightened spooked eyes, huge and wide with tiny irises, brows raised high and uneven, trembling look",
    "_half":      "eyes half closed mid-blink: upper eyelids lowered straight across covering the top half of the eyes, brows relaxed",
    "_closed":    "eyes fully closed, drawn as two gentle downward-curved closed-eyelid lines with small lashes, brows relaxed",
}

VISEMES = {
    "a_e":       "mouth open medium-wide for an 'ah'/'eh' sound, upper row of teeth visible, dark inside",
    "d_j_ch":    "lips parted slightly for a 'd'/'j'/'ch' sound, teeth together and visible between the lips",
    "f":         "an 'f'/'v' sound: upper teeth resting on the lower lip, lips slightly parted",
    "l":         "mouth open medium for an 'l' sound, tongue tip visible raised to the upper teeth",
    "m_b_close": "lips fully closed together for an 'm'/'b'/'p' sound",
    "o_big":     "mouth wide open in a big round 'oh' shape, large round dark opening",
    "o_small":   "lips pushed into a small tight round 'oo' shape, tiny round opening",
    "oh":        "lips rounded into a medium 'oh' shape, medium round opening",
    "th":        "mouth slightly open for a 'th' sound, tongue tip visible between the teeth",
    "trans":     "mouth relaxed and only very slightly open, neutral in-between-sounds shape",
}
MOOD = {"h": "with the mouth corners turned gently UP in a friendly smiling way",
        "s": "with the mouth corners turned DOWN in a sad unhappy way"}

BODIES = {
    "explain":      "her right arm (viewer's left) bent at the elbow with the open hand held out to the side, palm up, as if explaining a point; the other arm relaxed at her side",
    "question":     "both arms bent at the elbows with both open hands held out to the sides, palms up, shrugging as if asking a question",
    "thinking":     "one hand raised with the index finger and thumb touching her chin in a thinking gesture, the other arm folded across her waist",
    "idea":         "her left arm (viewer's right) raised with the index finger pointing straight up beside her shoulder, hand at shoulder height well away from the head, the other arm relaxed; a small yellow lightbulb floating beside the raised finger",
    "hi":           "her left arm (viewer's right) raised high to the side, waving with an open palm facing the camera, hand well away from the head; the other arm relaxed at her side",
    "pointing":     "her left arm (viewer's right) fully extended straight out to the side, index finger pointing to the side; the other arm relaxed",
    "you":          "her left arm (viewer's right) extended forward toward the camera, index finger pointing at the viewer; the other arm relaxed",
    "me":           "her right hand (viewer's left) placed flat on her chest over the heart, the other arm relaxed at her side",
    "winner":       "both arms raised high and out to the sides in a wide V of triumph, both hands as fists, arms clear of the head",
    "joy":          "both arms raised out to the sides at shoulder height with open palms up, joyful celebrating posture, arms clear of the head",
    "feeling_down": "shoulders slumped, both arms hanging down with the hands clasped together low in front of her, dejected posture",
    "paper":        "holding an open book with both hands in front of her stomach, reading it",
    "technical":    "holding a dark tablet computer with both hands in front of her stomach, screen facing the camera, no text on the screen",
    "meditation":   "sitting cross-legged, both hands resting palms-up on her knees with thumb and index finger touching, calm closed-mouth expression, eyes still open looking at camera, upright relaxed posture",
    "praying":      "both palms pressed together in front of her chest in a namaste/prayer gesture, elbows out slightly, calm posture",
    "kung_fu":      "a martial-arts fighting stance: one arm bent with the fist held up in front of her chest, the other arm bent with the fist pulled back at her hip, one leg stepped slightly forward, dynamic action pose",
    "sneaky":       "crouched slightly with knees bent, both arms bent close to her body with hands near her chest like tip-toeing, head tilted forward, a mischievous cautious posture",
}


def face_prompt(kind, key):
    if kind == "eyes":
        return KEEP + f"and change ONLY the eyes and eyebrows so they show: {EYES[key]}. Both eyes look straight at the camera. Keep the nose, mouth, face shape, hair and dupatta identical."
    vis, mood = key.rsplit("_", 1)
    return KEEP + f"and change ONLY the mouth so it shows: {VISEMES[vis]}, {MOOD[mood]}. Keep the eyes, eyebrows, nose, face shape, hair and dupatta identical."


def body_prompt(key):
    return (KEEP + "same head (neutral face looking at the camera), same dupatta on the head, same clothes, same feet position — "
            f"and change ONLY the arms and hands so that she is: {BODIES[key]}. Full body still visible, character still centred.")


def jobs(only=None):
    out = []
    ctx = f"{SRC}/context_M.png"
    if only in (None, "heads"):
        for d, side in (("L", "her left (viewer's right)"), ("R", "her right (viewer's left)")):
            out.append((f"{SRC}/head_{d}.png", KEEP + f"and turn her head and face a clearly visible 35-40 degrees toward {side}, a genuine three-quarter view: the far side of the face becomes noticeably narrower, the nose tip points toward {side}, the far eye and far eyebrow appear smaller and closer to the face outline, and the near ear is hidden while the tip of the far ear may show. This must look obviously turned, not front-facing. Keep a neutral closed-mouth expression and both eyes looking toward the camera. Keep the dupatta shape, hijab outline, shoulders and clothing in exactly the same place and size. Plain flat green background, no blur, no gradient, no vignette.", [ctx]))
    if only in (None, "eyes"):
        for k in EYES:
            out.append((f"{SRC}/eyes_{k}.png", face_prompt("eyes", k), [ctx]))
    if only in (None, "mouths"):
        for v in VISEMES:
            for m in "hs":
                out.append((f"{SRC}/mouth_{v}_{m}.png", face_prompt("mouth", f"{v}_{m}"), [ctx]))
    if only in (None, "bodies"):
        for b in BODIES:
            out.append((f"{SRC}/body_{b}.png", body_prompt(b), [PLATE]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only")
    ap.add_argument("--force", nargs="*", default=[], help="basenames (without .png) to regenerate")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    os.makedirs(SRC, exist_ok=True)
    ctx = f"{SRC}/context_M.png"
    if not os.path.exists(ctx):
        Image.open(PLATE).crop(CONTEXT).save(ctx)
    todo = [(o, p, i) for o, p, i in jobs(a.only)
            if not os.path.exists(o) or os.path.splitext(os.path.basename(o))[0] in a.force]
    json.dump({os.path.basename(o): p for o, p, _ in jobs()}, open(f"{BUILD}/prompts_used.json", "w"), indent=1)
    print(f"{len(todo)} images to generate (calls so far {calls()})")

    def run(job):
        o, p, i = job
        try:
            gen(p, o, images=i)
            return o, "ok"
        except Exception as ex:  # noqa: BLE001
            return o, repr(ex)[:120]
    with ThreadPoolExecutor(a.workers) as ex:
        for o, st in ex.map(run, todo):
            print(st, os.path.basename(o))
    print("total calls", calls())


if __name__ == "__main__":
    main()
