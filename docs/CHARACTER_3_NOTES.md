# character_3 build notes (2026-09-11) — "Ustani", Gemini-generated

Route A (Gemini plate + masked edits + fixed crop boxes), the option `docs/CHARACTER_2_NOTES.md`
left on the table for character_2. Kamal rejected character_2-style code-drawn art for a new
character ("bad character, why didn't you use the Gemini api for good quality") — this is that.

## Phase 0 — why Route A this time

character_2's PIL rig is precise but visually plain. The brief asked for an "appealing,
professional flat-illustration" look with `gemini-2.5-flash-image`, keeping character_2's
coordinate-model discipline (fixed crop boxes, one alignment pass, nothing hand-tuned per frame)
so misalignment — the stated failure mode — still can't happen by construction.

## Phase 1 — base plate

Prompt in `core/build/char3/plate_prompt_v1.txt`. Won on the FIRST generation (no reroll needed):
flat vector, thick dark outline, warm friendly Pakistani teacher, teal kameez, mustard dupatta
worn over the hair (modest, reads as a hijab), flat `#00FF00` background. Plate is 864x1184
(model's own aspect choice, not the 1920x1080 asked for — irrelevant, every downstream box is
derived from the plate's own coordinate space, not an assumed canvas size).

## Phase 2 — the two real gotchas (read before extending this character)

1. **Gemini's image-edit canvas is NOT a resize of the input.** Editing a small crop
   (`context_M.png`, 380x500, the CONTEXT box `(236,60,616,560)` on the plate) always comes back
   896x1152 — verified across all 16 eyes edits, 20 mouth edits, and both head_L/R turns. A
   naively cropped+resized `head_M` (from the plate, not an edit) landed ~13px off that canvas
   at the face silhouette, which was enough for a CLOSED-eyes paste to only cover the eyebrows
   and leave the head's own open eyes visible underneath (the bug looked like "blinking doesn't
   work" — it was actually a base-canvas mismatch). Fix: `head_M` is `eyes_happy.png` itself
   (any context-edit output works — its own baked eyes/mouth get fully overwritten by whatever
   gets pasted anyway), never a plate crop.
2. **Iris-blob detection must filter by size/shape, not just "biggest dark blob".** The first
   `find_eye_mouth_boxes()` picked the two biggest dark blobs in the upper face as "irises" —
   those were actually the hair/fringe shadow masses, both near the nose bridge, collapsing the
   eye box to a narrow strip that missed both eyes' outer thirds. Fix: filter blobs to a
   plausible iris area range (0.3%–3% of face area) and roughly-circular aspect (`0.6 < w/h <
   1.6`) before picking the top 2 by area. See `tools/build_character_3.py:find_eye_mouth_boxes`.

Both were caught by actually compositing a test frame and looking at it (`/tmp/blink_test_*.png`
pattern), not by the structural QA gate alone — the gate only checks boxes are *inside* the head
canvas, not that they land on the right feature. Re-run a manual blink composite after touching
`find_eye_mouth_boxes` on any future character.

## Phase 3 — what's fixed vs. re-derived

- `CONTEXT = (236,60,616,560)` on the plate is the head-edit crop AND (unscaled) the body's
  head-paste box — bodies are edits of the FULL plate (864x1184, same coordinate space as
  CONTEXT), so the head slot never needs re-alignment, it's the same box by construction.
- `eye_box`/`mouth_box` are derived ONCE from `eyes_happy.png` / `mouth_m_b_close_h.png` and
  reused for all 14 emotions x blink states and 10 visemes x 2 moods — this only works because
  every context-edit output shares the 896x1152 canvas AND near-identical face bbox (checked:
  eyes_happy vs eyes_sad bbox differs by 3px, closed/half by 0px). No per-emotion re-detection.
- Body head-cut: blank the CONTEXT-box COLUMN (not the whole row) above the collar line
  (`CONTEXT[3]-15`) before pasting the separate head on top. Blanking the whole row was the first
  attempt and it silently deleted raised arms in `winner`/`hi`/`idea`/etc. (anything above the
  collar that isn't the head) — always column-scope the cut for a full-body character.
- `_2` intensity folders reuse the base emotion's PNG (no separate "intensity 2" Gemini call) —
  documented behaviour, not a shortcut bug. Blink 02/04 = half, 03 = closed, from one `eyes__half`
  / `eyes__closed` edit pair, reused by every emotion.

## Phase 4 — body pose coverage

13 poses generated to cover 39 `body_actions` (see `POSE_MAP` in `build_character_3.py`):
explain, question, thinking, idea, hi, pointing→"you", winner, joy, feeling_down, paper,
technical, meditation, praying, kung_fu, sneaky. `standing` group (chilling/meditation-before-fix/
shy/sneaky-before-fix) fell back to the plate itself. A harsh second-opinion agent pass (see
Phase 5) flagged `kung_fu`/`meditation`/`praying`/`sneaky` as not reading as their label when they
were folded into `winner`/`standing`/`hi` — 4 more targeted poses were generated (58 Gemini calls
total for the whole character, still comfortably under the ~80-call budget) and `POSE_MAP`
updated to route them to themselves instead of a lookalike.

`meditation` and `sneaky` change the character's overall silhouette height (sitting cross-legged,
crouching) — the body-paste box is one fixed rect shared by every pose, so these two end up
looking like the character is "floating" slightly above the desk/chair line rather than planted on
it. Confirmed NOT a floating-head or double-head bug (checked full un-zoomed composites for both)
— just a proportion quirk of applying one fixed anchor to poses with a different overall height.
Acceptable for now; a real fix would need a per-pose vertical offset in the body metadata.

## Phase 5 — QA

`tools/character_qa.py character_3`: 0 structural FAILs (after the two Phase-2 fixes). Visual
review: all 5 `faces_zoom_*.png` sheets clean (eyes in face, mouth under nose, no green fringe, no
seam rectangles). `blink_zoom.png` clean after the Phase-2 fixes (open→half→closed→half, no eye
displacement). `bodies_01/02.png`: heads sit on the collar in every one of the 39 actions, no
floating/disconnected hands.

Independent harsh-critic pass (separate Sonnet agent, given only the QA sheet paths): faces/blink
sheets clean; flagged kung_fu/meditation/praying/sneaky/winner pose-reading issues. winner turned
out fine on closer (full-resolution) inspection — the thumbnail sheet is too small to resolve
closed fists; the other four were genuine POSE_MAP mismatches, fixed in Phase 4.

## Phase 6 — test render

`example/story/ustani-short.txt` (202 chars, mentions "Ustani"). First run: LLM picked character_3
for 39/40 words, word 0 ("Assalam") fell back to character_1 (the same known first-word gotcha
documented for character_2). Patched `character_3=3` for every word in both
`build/ustani_test/output_test.json` and the `Character` column of `video_frames_info.csv`
(frame_generator reads the CSV, not the JSON), re-ran with `--skip-core` — 410/410 frames on
character_3. `build/ustani_test/final.mp4`: 1920x1080, 16.16s, mpeg4 video + AAC audio, muxed with
ffmpeg. 4 preview frames pulled at 2s/6s/10s/14s — all clean: head on collar, eyes/mouth in place,
"winner" pose's raised fists legible at full resolution (contradicting the thumbnail-scale QA
critique above).

## Gemini call budget

58 calls in `build/char3/calls.log` (0 failures) + 2 ad-hoc test calls before the pipeline
existed = ~60 total. Budget given was ~80.
