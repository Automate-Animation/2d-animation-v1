#!/usr/bin/env python3
"""Fire every remaining char4 Gemini job concurrently (thread pool) -- sequential calls take
~10min each on this network, so 49 remaining calls sequentially would take ~8h. Run from core/:
../.venv/bin/python tools/char4_run_all.py
"""
import concurrent.futures as cf
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tools.gemini_img as gi  # noqa: E402
import tools.char4_generate as g  # noqa: E402

JOBS = []


def add(out, prompt):
    if not os.path.exists(out):
        JOBS.append((out, prompt))


def build_jobs():
    add(f"{g.SRC}/head_blank.png", None)  # filled below via g.build_head's prompt string
    # reuse the exact prompt strings from char4_generate by calling its internal builders in dry mode
    return


def run_job(out, prompt):
    try:
        gi.gen(prompt, out, images=[g.REF])
        g._log(out, True)
        return out, True, ""
    except Exception as ex:  # noqa: BLE001
        g._log(out, False, str(ex)[:200])
        return out, False, str(ex)[:200]


def main():
    # Build the full job list by calling the same prompt-construction logic as char4_generate.py
    jobs = []

    # head
    head_prompt = (f"Edit this character sticker: crop to HEAD AND NECK ONLY (shoulders barely visible), "
                   f"then REMOVE the eyes, eyebrows and mouth completely -- replace that area with smooth "
                   f"plain skin, warm tan skin tone, keep the nose, keep the hairstyle and hair colour, keep "
                   f"ears. A perfectly blank featureless face from eyebrow-line to chin except the nose. "
                   f"{g.STYLE}. Solid flat pure green background (#00FF00), no shadow.")
    jobs.append((f"{g.SRC}/head_blank.png", head_prompt))

    for vis, desc in g.VISEME_DESC.items():
        for mood, suf in (("happy", "h"), ("sad", "s")):
            mood_word = "cheerful happy mood" if suf == "h" else "sad downturned mood, flatter lower lip"
            prompt = (f"Generate ONLY a sticker of this character's MOUTH -- lips, teeth and tongue only, "
                      f"nothing else. {desc}. {mood_word}. Skin/lip colour matches the reference character's "
                      f"warm tan skin tone and natural lip colour. Absolutely NO skin patch around it, NO nose, "
                      f"NO cheeks, NO chin outline -- just the isolated mouth shape as a small sticker, thick "
                      f"clean black outline, flat colours, matching the reference's art style. Centered on a "
                      f"solid flat pure green background (#00FF00).")
            jobs.append((f"{g.SRC}/mouth_{vis}_{suf}.png", prompt))

    for emo in g.EMOTIONS:
        prompt = (f"Generate ONLY a sticker of this character's EYES AND EYEBROWS showing the '{emo}' emotion, "
                  f"looking straight ahead at the viewer. Two eyes with eyebrows, expressive line art, "
                  f"same art style as the reference (thick black outlines, flat colours), same eye/iris colour "
                  f"as the reference character. Absolutely NO skin around them, NO nose, NO face outline -- just "
                  f"the isolated eyes+eyebrows sticker. Solid flat pure green background (#00FF00).")
        jobs.append((f"{g.SRC}/eyes_{emo}.png", prompt))

    jobs.append((f"{g.SRC}/lids_upper.png",
                 "Generate ONLY a sticker of a pair of closing eyelids -- just the upper eyelid shapes "
                 "starting to close over open eyes, same skin tone as reference, thick black outline, "
                 "flat colours, matching the reference character's art style. No other facial features. "
                 "Solid flat pure green background (#00FF00)."))
    jobs.append((f"{g.SRC}/lids_closed.png",
                 "Generate ONLY a sticker of a pair of fully closed eyes -- two simple closed-eyelid curved "
                 "lines with eyelashes, same skin tone as reference, thick black outline, flat colours, "
                 "matching the reference character's art style. No other facial features. "
                 "Solid flat pure green background (#00FF00)."))
    jobs.append((f"{g.SRC}/lids_half.png",
                 "Generate ONLY a sticker of a pair of half-open eyes reopening from a blink -- upper lids "
                 "half down AND lower eyelid curves drawn, same skin tone as reference, thick black outline, "
                 "flat colours, matching the reference character's art style. No other facial features. "
                 "Solid flat pure green background (#00FF00)."))

    for name, desc in g.POSES.items():
        prompt = (f"Edit this character: same clothing and colours ({g.PALETTE}), but generate a HEADLESS "
                  f"full body sticker -- remove the head completely, leave a visible flat neck stump where "
                  f"the neck was cut, same body framing and scale as the reference (full body, same camera "
                  f"distance). Pose: {desc}. {g.STYLE}. Solid flat pure green background (#00FF00), no ground "
                  f"shadow.")
        jobs.append((f"{g.SRC}/body_{name}.png", prompt))

    jobs = [(o, p) for o, p in jobs if not os.path.exists(o)]
    print(f"{len(jobs)} jobs to run")
    t0 = time.time()
    done = 0
    with cf.ThreadPoolExecutor(max_workers=14) as ex:
        futs = {ex.submit(run_job, o, p): o for o, p in jobs}
        for fut in cf.as_completed(futs):
            out, ok, note = fut.result()
            done += 1
            print(f"[{done}/{len(jobs)}] {'OK' if ok else 'FAIL'} {out} {note} ({time.time()-t0:.0f}s elapsed)", flush=True)
    print("ALL_JOBS_DONE")


if __name__ == "__main__":
    main()
