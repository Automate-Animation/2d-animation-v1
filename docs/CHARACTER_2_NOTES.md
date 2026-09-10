# character_2 build notes (2026-09-10)

Working log for the second synctoon character. Written as decisions were made.

## Phase 0 — how the CURRENT loader composes a frame (CharacterManager.get_character)

1. `head` = random PNG in `head/<Head_Direction>/` (L|M|R). No metadata; canvas used as-is.
2. `eyes` = `eyes/<Emotion>/<Emotion>_<Eyes_Direction>.png`, or when blink
   `eyes/<Emotion>/<Emotion>_blink/<Eyes_Direction>.png` — the CSV writes `02`,`03`,`04` for the
   3 blink frames. **frame_generator.py:44 does `bool(row["Blink"])`, which is True for the string
   "False"**, so the `_blink/` folder path is ALWAYS used -> every `<emotion>_blink/` folder must also
   contain `<emotion>_L/M/R.png` (6 files, not 3). Metadata key = emotion folder (`asset_name = asset_sub_type`),
   NOT the file. `<Emotion>` is `emotions[id]` or `emotions[id] + "_2"` when intensity == 2
   (update_character_asset_name.py) -> 28 eye folders.
3. `mouth` = `mouth/<happy|sad>/<name>.png`; metadata key = file stem (`a_e_h` ...). Pasted with **mirror=True**.
   Mouth emotion: happy for {happy, content, sarcasm, crazy, evil_laugh, lust, silly} (+ `_2`), else sad.
   10 visemes: a_e d_j_ch f l m_b_close o_big o_small oh th trans, suffix `_h`/`_s`.
4. eyes then mouth pasted onto head at `metadata[eyes|mouth][key].position` resized to `.size`.
5. `body` = random PNG in `body/<Body>/`; metadata key = **file stem** (`body15`), so the head anchor is per FILE.
   Head pasted onto body at `metadata.body[stem].position/size`.
6. `background` = random PNG in `background/<name>/`; metadata key = file stem. Body pasted with **mirror=True**
   at `.position/.size`; `zoom_point` used when zoom in 1..7.
7. `adding_image` uses `img.resize(size)` with no aspect protection -> any mismatch between canvas and
   metadata.size distorts the layer (char_1: 93x96 eyes -> 250x150, 800x1080 body -> 750x1080).

### character_1 facts (reference)
- head 359x293 RGBA (yellow blob, 3 angles nearly identical), eyes 93x96..236x182 (varies by emotion),
  mouth 53x62..420x43 (varies), body 800x1080 (headless stick figure, neck at ~(400,300)), background 1920x1080.
- body metadata e.g. `body33` (standing) size [285,255] position [230,25] -> head box x230..515 y25..280.
- background: body size [750,1080] at position [250,160] -> bottom 160px of the body are clipped off-frame.
- eyes: 25/28 entries identical {position [10,30], size [250,150]}. mouth block has 26 dead emotion keys.
- Pre-existing defects seen: `background/garden/` contains `gardan.png` but metadata key is `garden` ->
  KeyError for screen_mode 16 on character_1 (the old `gardan/` folder was deleted in the working tree today).
- constants: 14 emotions, 39 distinct body_action names (47 ids, dupes), 31 screen modes.

## Phase 1 — route decision
**Route B: code-drawn PIL vector rig** (`core/tools/build_character_2.py`).
Reason: every layer is drawn at a fixed coordinate in its own canvas, and metadata `size` == canvas size
(scale 1) so nothing is stretched; eye/mouth boxes are constants shared by all 28 emotion folders and 20
visemes; the body head-anchor is the same constant for all poses (torso never moves, only arms/props),
so "nothing floats" is true by construction and the QA gate can assert it. cairosvg is not installed in
`.venv`, so shapes are PIL primitives drawn at 4x and downsampled (LANCZOS) for anti-aliasing.
Route A (Gemini edits) rejected for v1: identity/proportion drift across ~60 edits is exactly the failure
mode Kamal flagged, and there is no rembg for cleanup. It stays an option for a head re-skin later.

## Canvas / coordinate model (character_2)
- head   360x300  (char_1 359x293, same ballpark). Face oval centre (180,150). Neck drawn to canvas bottom.
- eyes   250x130  pasted at head (55,62)   -> eye centres head (125,140) & (235,140)
- mouth  110x55   pasted at head (125,205) -> mouth centre head (180,232)   [eyes box bottom 192 < mouth top 205]
- body   800x1080 headless; neck top / head anchor at body (400,350); head pasted at (220,50) size [360,300]
  (feeling_down/shy: y +12 to read as a lowered head). Extra per-body key `neck` stored for QA only (loader ignores it).
- background 1920x1080; body pasted at (560,0) size [800,1080] (scale 1, nothing clipped), zoom_point [960,200] (head).

## Phase 2 — assets produced (`core/tools/build_character_2.py`)
346 files: 3 heads, 252 eyes (28 folders x [L,M,R + blink/{02,03,04,L,M,R}]), 20 mouths, 39 bodies (one PNG per
distinct action, file stem == action), 32 backgrounds (31 screen modes + `gardan` alias; plates copied from
character_1, renamed to `<name>.png` so the metadata key equals the folder). metadata.json["character_2"] written by
the builder; constants.characters got `2: {"name": "Teacher", "type": "Educator"}`.
Backgrounds are copies (61 MB) rather than re-colours: the loader needs a per-character folder and the plates are
already 1920x1080; re-colouring would add nothing.
Also today: restored `character_1/background/gardan/gardan.png` (deleted in the working tree before this session),
renamed the untracked `garden/gardan.png` -> `garden/garden.png`, and added a `gardan` key to character_1 metadata,
so both names resolve for both characters (verified with get_character).

## Phase 3 — QA gate (`core/tools/character_qa.py`, sheets in `core/build/qa/character_2/`)
Round 1 (0 structural FAILs, visual review): faint rectangles above/below every eye (anti-aliased skin-coloured
lid patches), grey blush (translucent paint on an RGBA canvas is not blended), elbows bending inward on
paper/technical/chilling. Fixed: eyelids are now masks on the eyeball, blush pre-blended opaque, elbow side auto.
Round 2: bore_2 / glare_2 / sarcasm_2 collapsed to identical slits and spoked was a shock clone. Fixed: intensity-2
openness floored at 0.3, lid drop capped, spoked given asymmetric brows/pupils.
Round 3: 0 FAILs, all 84 emotion x head tiles and 39 body tiles reviewed at 2x crop — clean.
Still imperfect (P2): feeling_down differs from standing only by lowered head + inward hands; lust reads as "smug";
hi/open hands are stubby at 1080p.
character_1 through the same gate: `metadata.background[gardan] missing` (pre-existing, now patched) and the neck
heuristic fails on ~40 bodies because the PNGs carry stray corner registration marks at the top rows, so the
"first opaque row" is not the neck. Not fixed (out of scope); new characters carry an explicit `neck` key instead.

## Phase 4 — test render (2026-09-10 16:14–16:19, LLM_PROVIDER=claude-cli, LLM_MODEL=haiku)
`python -u create_animation.py --script ../example/story/teacher-short.txt -n teacher_test` -> 386 frames, 258 s total.
The LLM picked character 2 for 42/43 words (the very first word "Good" fell back to the default 1 -> ~0.4 s of Hero
at t=0; fix: set `"character": 2` on that word in output_test.json and rerun with --skip-core). Backgrounds chosen:
classroom + office; bodies achieve/chilling/question/why/explain; emotions happy/content; zoom 1-2 used.
Outputs copied to `core/build/qa/teacher_test_render/`: teacher_test.mp4 (raw cv2 mp4v), teacher_test_av.mp4
(h264 + AAC from voice.mp3: 1920x1080, 15.58 s), frame_1s/5s/9s/13s.png — all four frames clean (head on collar,
eyes/mouth in place, zoom frames correct). Raw cv2 mp4v file: 386/386 frames decodable once the writer had finalised (an earlier copy taken 12 s too early was truncated).
