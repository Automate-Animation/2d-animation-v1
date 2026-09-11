#!/usr/bin/env python3
"""Generate character_4 ('Sir Ahmed') Gemini source stickers into build/char4/src/.
Route: parts-as-stickers (SKILL.md sec 3) -- NOT plate+fixed-box-cut (that was character_3's mistake).
Every call passes the style reference PNG as inlineData + repeats the palette hex codes.
Re-runnable: skips any output file that already exists. Logs to build/char4/calls.log (separate from char3).
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tools.gemini_img as gi  # noqa: E402

SRC = "build/char4/src"
REF = f"{SRC}/reference.png"
LOG = "build/char4/calls.log"

PALETTE = ("kurta light-blue #A9D6E5 with #6FB6D9 shading, navy waistcoat #1E2A4A, "
           "dark grey trousers #3B3F47, warm tan skin #C98E5E, short black hair #1A1A1A")

STYLE = ("thick clean black outlines, flat cel-shaded colours (2-3 tone shading only), "
         "bold sticker-style digital illustration, same exact character design as the reference image")


def _log(name, ok, note=""):
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a") as f:
        f.write(f"{time.strftime('%H:%M:%S')}\t{name}\t{'ok' if ok else 'FAIL'}\t{note}\n")


def gen_once(out, prompt, images=(REF,)):
    if os.path.exists(out):
        print("skip (exists)", out)
        return out
    try:
        gi.gen(prompt, out, images=list(images))
        _log(out, True)
        print("OK", out)
    except Exception as ex:  # noqa: BLE001
        _log(out, False, str(ex)[:200])
        print("FAIL", out, ex)
    return out


VISEME_DESC = {
    "a_e": "wide open smile mouth, upper and lower teeth both visible, corners pulled up",
    "d_j_ch": "teeth held together, lips parted slightly, relaxed",
    "f": "upper teeth resting on lower lip",
    "l": "mouth open, tongue tip visible touching upper teeth",
    "m_b_close": "lips fully closed pressed together, a simple closed line, no teeth visible",
    "o_big": "mouth wide open, round shape, big O shape, teeth barely visible",
    "o_small": "mouth open, small round shape, smaller O",
    "oh": "mouth open, oval vertical shape",
    "th": "tongue visible between the front teeth, mouth slightly open",
    "trans": "mouth relaxed, half open, neutral in-between shape",
}

EMOTIONS = ["happy", "sad", "angry", "bore", "content", "glare", "sarcasm", "worried",
            "crazy", "evil_laugh", "lust", "shock", "silly", "spoked"]


def build_reference():
    prompt = open("build/char4/prompt_reference.txt").read()
    if not os.path.exists(REF):
        if os.path.exists(f"{SRC}/reference_raw.png"):
            os.rename(f"{SRC}/reference_raw.png", REF)
        else:
            gen_once(REF, prompt, images=())
    print("reference ready:", os.path.exists(REF))


def build_head():
    prompt = (f"Edit this character sticker: crop to HEAD AND NECK ONLY (shoulders barely visible), "
              f"then REMOVE the eyes, eyebrows and mouth completely -- replace that area with smooth "
              f"plain skin, same {PALETTE.split(',')[3].strip()} tone, keep the nose, keep the hairstyle "
              f"and hair colour, keep ears. A perfectly blank featureless face from eyebrow-line to chin "
              f"except the nose. {STYLE}. Solid flat pure green background (#00FF00), no shadow.")
    gen_once(f"{SRC}/head_blank.png", prompt)


def build_mouths():
    for vis, desc in VISEME_DESC.items():
        for mood, suf in (("happy", "h"), ("sad", "s")):
            mood_word = "cheerful happy mood" if suf == "h" else "sad downturned mood, flatter lower lip"
            prompt = (f"Generate ONLY a sticker of this character's MOUTH -- lips, teeth and tongue only, "
                      f"nothing else. {desc}. {mood_word}. Skin/lip colour matches the reference character's "
                      f"warm tan skin tone and natural lip colour. Absolutely NO skin patch around it, NO nose, "
                      f"NO cheeks, NO chin outline -- just the isolated mouth shape as a small sticker, thick "
                      f"clean black outline, flat colours, matching the reference's art style. Centered on a "
                      f"solid flat pure green background (#00FF00).")
            gen_once(f"{SRC}/mouth_{vis}_{suf}.png", prompt)


def build_eyes():
    for emo in EMOTIONS:
        prompt = (f"Generate ONLY a sticker of this character's EYES AND EYEBROWS showing the '{emo}' emotion, "
                  f"looking straight ahead at the viewer. Two eyes with eyebrows, expressive line art, "
                  f"same art style as the reference (thick black outlines, flat colours), same eye/iris colour "
                  f"as the reference character. Absolutely NO skin around them, NO nose, NO face outline -- just "
                  f"the isolated eyes+eyebrows sticker. Solid flat pure green background (#00FF00).")
        gen_once(f"{SRC}/eyes_{emo}.png", prompt)
    # 3 shared lid stickers, reused across every emotion (character_1's approach)
    gen_once(f"{SRC}/lids_upper.png",
             "Generate ONLY a sticker of a pair of closing eyelids -- just the upper eyelid shapes "
             "starting to close over open eyes, same skin tone as reference, thick black outline, "
             "flat colours, matching the reference character's art style. No other facial features. "
             "Solid flat pure green background (#00FF00).")
    gen_once(f"{SRC}/lids_closed.png",
             "Generate ONLY a sticker of a pair of fully closed eyes -- two simple closed-eyelid curved "
             "lines with eyelashes, same skin tone as reference, thick black outline, flat colours, "
             "matching the reference character's art style. No other facial features. "
             "Solid flat pure green background (#00FF00).")
    gen_once(f"{SRC}/lids_half.png",
             "Generate ONLY a sticker of a pair of half-open eyes reopening from a blink -- upper lids "
             "half down AND lower eyelid curves drawn, same skin tone as reference, thick black outline, "
             "flat colours, matching the reference character's art style. No other facial features. "
             "Solid flat pure green background (#00FF00).")


POSES = {
    "explain": "standing, one hand raised with palm up as if explaining a concept, gesturing forward",
    "question": "standing, both hands out to the sides palms up, shoulders slightly raised, questioning gesture",
    "thinking": "standing, one hand touching the chin area (touching the neck stump), head-tilt body lean, thinking pose",
    "idea": "standing, one arm raised straight up with a hand open as if holding a lightbulb above it, excited pose",
    "hi": "standing, one arm raised waving hello, palm facing forward",
    "standing": "standing straight, arms relaxed at sides, neutral resting pose",
    "pointing": "standing, one arm extended forward pointing with index finger",
    "winner": "standing, both arms raised up in a victory cheer, fists or open hands up",
    "feeling_down": "standing, shoulders slumped, arms hanging low, dejected slouched posture",
    "confuse": "standing, one hand scratching the back of the neck stump, shoulders shrugged, confused posture",
    "joy": "standing, arms spread wide open, chest out, joyful open posture",
    "technical": "standing, one hand near the neck stump as if adjusting glasses, other hand holding a small clipboard, focused posture",
}


def build_bodies():
    for name, desc in POSES.items():
        prompt = (f"Edit this character: same clothing and colours ({PALETTE}), but generate a HEADLESS "
                  f"full body sticker -- remove the head completely, leave a visible flat neck stump where "
                  f"the neck was cut, same body framing and scale as the reference (full body, same camera "
                  f"distance). Pose: {desc}. {STYLE}. Solid flat pure green background (#00FF00), no ground "
                  f"shadow.")
        gen_once(f"{SRC}/body_{name}.png", prompt)


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else "all"
    if only in ("all", "reference"):
        build_reference()
    if only in ("all", "head"):
        build_head()
    if only in ("all", "mouths"):
        build_mouths()
    if only in ("all", "eyes"):
        build_eyes()
    if only in ("all", "bodies"):
        build_bodies()
    n = sum(1 for _ in open(LOG)) if os.path.exists(LOG) else 0
    print(f"calls logged so far (char4): {n}")


if __name__ == "__main__":
    main()
