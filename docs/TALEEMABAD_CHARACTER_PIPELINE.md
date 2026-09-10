# Taleemabad character pipeline: persona reference -> synctoon rig

Status: plan (2026-09-10). Companion to `docs/ASSET_FORMAT.md` (defines `character.json`, visemes A-H+X, tags,
`timeline.json`). Target: teacher/student personas for Taleemabad University videos, 1920x1080 @ 24 fps
(`canvas` in `character.json`; `FRAME_PER_SECOUND=24` in `add_phonemes.py`).

## 0. Pipeline at a glance

```
persona wizard (Design-your-perfect-AI-Persona)  -> reference PNG (front/side/back, 16:9 1K, nano-banana-pro)
  -> 1. base plate: front view, T-pose, neutral face, flat green, fixed 1080-high canvas   (1 image-edit call)
  -> 2. variants by masked image-edit from the base plate                                 (N calls, see counts)
  -> 3. cut + align: chroma-key -> transparent PNG; anchors by diff-landmarking (+ mediapipe as a check)
  -> 4. build character.json (tags from filenames, pivots/anchors from step 3)
  -> 5. QA contact PNG (every layer composited on the head/body) -> human eyeball
  -> 6. register: characters/<id>/ + validator; timeline generator now reads tags for allowed emotions/gestures
```

Constraint that drives everything: identity has to survive ~60-150 generations. Local SD failed at this for Rumi
(memory: "Local ImageGen Verdict"), so every variant is a **cloud image-edit of the same base plate** (Gemini
`nano-banana-pro-preview`, already used in `server.ts`; or Kie.ai nano-banana via the `kie-ai-imagegen` skill as
the cheaper batch route). Never text-to-image a variant from scratch.

## 1. Persona tool -> reference image

Today `server.ts` has one endpoint `POST /api/generate-avatar`: `gemini-2.5-flash` expands `AvatarConfig`
(`src/types.ts`: headShape, eyes, mouth, hair, bodyShape, clothing, artDirection, ...) into a `masterPrompt`, then
`nano-banana-pro-preview` renders a 16:9 "multi-angle character reference" and returns a data URL. That image
is the identity document. Keep it; it is input to step 1, not a layer source (views are not on a flat colour and
share one canvas).

Taleemabad persona defaults (put them in the wizard as a "Taleemabad teacher / student" preset): flat 2D
vector-cartoon style with clean black outlines (matches character_1's look and chroma-keys cleanly), shalwar
kameez/dupatta or school uniform, no text on clothing, plain solid-colour palette (<= 6 colours so edits stay
consistent), age-appropriate proportions, no jewellery detail that will smear at 93 px eye size.

## 2. What to generate per character

Naming convention (filenames are data only via tags, but the builder derives tags from names):
```
head/head_<angle>.png                    angle in {M,L,R}          e.g. head_M.png
eyes/eyes_<emotion>_<gaze>.png           gaze in {M,L,R,down}      eyes_happy_M.png
eyes/eyes_<emotion>_blink<1..3>.png      1 = half, 2 = closed, 3 = half-open   eyes_happy_blink2.png
mouth/mouth_<viseme>_<emotion>.png       viseme in {A..H,X}, emotion in {neutral,happy,sad}   mouth_C_neutral.png
body/body_<gesture>[_<variant>].png      body_explain.png, body_explain_2.png
```
Everything is authored on the same canvas as the base plate (body 1080 px tall, head ~300 px), so `scale = 1.0`
in `character.json` and no per-asset `size` exists. The canvas is the proportion lock.

| Layer | Minimum viable character (MVC) | Full |
|---|---|---|
| head | 1 (M) | 3 (M, L, R) |
| eyes | 1 emotion x 1 gaze + blink (half, closed) = 3 | 6 emotions (neutral, happy, sad, surprised, thinking, stern) x 3 gaze = 18, + 2 blink frames per emotion = 30 (20 if one shared blink pair) |
| mouth | 9 visemes x neutral = 9 (G,H may reuse B,C -> 7) | 9 x 3 emotions = 27 |
| body | 3 gestures (standing, explain, point) | 12 (standing, explain, point-left, point-right, hold-book, write, think, wave, thumbs-up, arms-crossed, sit-desk, walk) x 1-2 variants |
| **layers total** | **16** | **~90-100** |

Image-gen calls (one call can carry a grid strip that is cut afterwards; strips keep identity better than single
mouths because the model sees the face while drawing them):
- MVC: 1 base plate + 1 head crop (M) + 1 eyes strip (open, half, closed) + 1 mouth strip (3x3 = 9 visemes)
  + 3 bodies + 2 diff-landmark plates = **9 calls**, plus ~30% rerolls -> **~12 calls**. At nano-banana-pro list
  price (about USD 0.13 per 1K image; Kie nano-banana is cheaper) that is roughly USD 1-2 per MVC.
- Full: 1 + 3 heads + 6 eyes strips + 3 mouth strips + 12-24 bodies + 2 = **27-39 calls**, with rerolls **~50**,
  i.e. under USD 10 per character. Individual (non-strip) generation would be ~150 calls; do not do that.

## 3. Layer generation recipes (image-edit with masks)

All edits: input = base plate (front, T-pose, neutral, flat green `#00FF00`, 1920x1080, character centred, feet at
y=1040) + a hard mask of the region to change + prompt "keep everything outside the mask pixel-identical".

1. **Base plate**: from the reference image: "redraw the FRONT view only, full body, T-pose, arms 30 deg from the
   body, neutral closed mouth (viseme X), eyes open looking at camera, flat green background, no shadow, centred".
2. **Heads L/M/R**: mask = head + neck. M is a crop of the base plate. L/R: "turn the head 30 deg left/right,
   same hair, same outline weight, keep the neck position". Reject if the neck base moves more than 6 px (measured
   by the alpha bottom edge after keying). Prefer **R = mirror of L** only if the design is symmetric (parting,
   badge, dupatta usually are not; that is why `flip` is per asset in `character.json`).
3. **Eyes**: mask = eye region on head M. One strip per emotion: "a 1x5 strip: open-centre, open-left,
   open-right, half-closed, closed, identical size and position in each cell". Cut cells by the grid. Half-open
   frame 3 of the blink can be the half-closed cell reused (blink = half, closed, half).
4. **Mouths**: mask = mouth region. One 3x3 strip per emotion, cells labelled in the prompt with the Rhubarb
   descriptions (A closed pressed, B slightly open teeth, C open, D wide open, E slightly rounded, F puckered,
   G teeth on lower lip, H tongue up, X relaxed closed). Ask for identical lip-corner positions per cell so the
   pivot is stable.
5. **Bodies**: mask = everything below the neck line. Prompt per gesture, "headless: end the neck at the collar
   with a flat cut", same clothing colours. If the model refuses headless, generate with the head and crop at the
   neck line detected from the base plate; the head layer covers the seam.
6. **Backgrounds**: text-to-image once per scene (classroom, staff room, home study, whiteboard close-up,
   flat colours), 1920x1080, shared across characters; add to `backgrounds.json` with a `stage.anchor`.

Consistency checks run on every output before it is accepted (script, stdlib+PIL+numpy):
palette distance to base plate (mean of the 6 dominant colours), outline thickness (median stroke width via
erosion), body bbox height within 2% of the base plate, head bbox within 3%. Fail -> reroll with the same seed
+1, max 3 tries, then flag for a human.

## 4. Auto-cut and alignment

- **Cut**: we control the background, so chroma-key beats `rembg`: alpha = 0 where
  `|G-255|<40 and R<80 and B<80`, feather 1 px, then despill green from edge pixels. Keep `rembg` (u2net) only for
  the imported reference image where the bg is not flat. Both are one function each.
- **Landmarks (anchors)**: cartoon faces break `mediapipe` face mesh often (character_1's head is a featureless
  ellipse). Primary method is **diff-landmarking**: ask the edit model for the head with eyes removed and for the
  head with mouth removed (the 2 extra calls counted above). `bbox(|head - head_no_eyes| > 8)` is the eyes
  anchor box; same for mouth. Anchor = bbox centre, pivot of every eye/mouth PNG = its own bbox centre, so the
  placement rule in `ASSET_FORMAT.md` section 4 holds with no hand-entered numbers.
  Secondary check: `mediapipe` face mesh on head M (landmarks 33/133/362/263 eye corners, 61/291 mouth corners,
  13/14 lips); if it detects and disagrees with the diff box by >10 px, print both and let the human pick.
- **Body head anchor**: neck top = topmost alpha row of the headless body at the horizontal centre of mass of the
  top 40 px; head pivot = the same point on head M (bottom of the chin/neck cut). One number per body pose, found
  automatically.
- **Stage**: body pivot = feet centre (bottom alpha row, centre); `stage.anchor` per background is where that lands.

## 5. Build `character.json`

`tools/build_character.py characters/<id>/` : walk the folder, parse names into tags (section 2), read pivots and
anchors from the sidecar `anchors.json` that step 4 writes, emit the manifest, run the schema validator
(`jsonschema` is already in `requirements.txt`), and refuse to write if any viseme A-F or X is missing for the
`neutral` emotion or if `head_M` lacks `eyes`/`mouth` anchors.

## 6. QA contact image

`tools/contact_grid.py characters/<id>/` -> `qa/<id>_grid.png`: row 1 = head M/L/R each with default eyes and
mouth X; row 2 = every eyes asset composited on head M; row 3 = 9 visemes on head M per emotion; row 4 = every
body with head attached, at 25%. Cell label = asset id. This is the artefact a human approves before registering.
It also doubles as the marketing "layer explosion" image.

## 7. Register in synctoon

Drop the folder under `core/images/characters/<id>/` with `character.json`; `CharacterManager` loads the manifest
instead of `metadata.json`; the timeline generator asks the manifest for allowed `gesture`/`emotion`/`gaze` tags
and passes that list to the Gemini text step in `core.py` (replacing `constants.emotions`/`body_actions`), so the
LLM cannot request an asset that does not exist. Backgrounds move to `core/images/backgrounds/`.

## 8. Taleemabad content constraints

- **Languages**: Urdu and English, often code-switched in one sentence. `g2p-en` (used in `add_phonemes.py`) is
  English-only and will mangle Urdu tokens; Gentle's acoustic model is English too.
- **English path**: keep Gentle (Docker) or use the ElevenLabs alignment output; map phones with the ARPAbet table.
- **Urdu path** (also code-switched lines): voice via ElevenLabs TTS `with-timestamps` (or `forced-alignment` for
  recorded audio). It returns per-character start/end times of the Urdu script. Map each character to a viseme
  with a fallback table: `ب پ م -> A`; `ف -> G`; `و (consonant) -> F`; `ل -> H`; `ا آ ع (long a) -> D`; `ی -> B`;
  `و (vowel) او -> F`; `ے ای -> C`; `ہ ح -> C`; other consonants (`ت ٹ د ڈ ک گ ق ج چ س ش ز ر ن ں خ غ ژ ث ص ض ط ظ`)
  `-> B`; diacritics adjust the vowel: zabar -> C, zer -> B, pesh -> F; spaces and punctuation -> X.
  Merge adjacent identical visemes and enforce a 2-frame minimum. Alternative that needs no text: run Rhubarb in
  phonetic mode on the WAV; it outputs A-H+X directly and is "good enough" for non-English speech.
- **Numbers and English words inside Urdu script** appear as Latin: route those tokens through `g2p-en`.
- **Look**: classroom-appropriate dress, no exaggerated `lust`/`evil_laugh`/`kung_fu` sets from character_1's
  `constants.py`; the manifest tags make the available emotion set explicit per character.
- **Duration**: lessons are 3-8 minutes -> 4k-12k frames; runs, not rows (ASSET_FORMAT section 7).

## 9. Phased build order

| Phase | Scope | Definition of done | Acceptance test (checkable) |
|---|---|---|---|
| 1. Format + renderer | `character.json`, `timeline.json`, validator, deterministic renderer, migrate character_1 | `python tools/migrate_metadata.py` produces `characters/character_1/character.json`; renderer reads timeline only; `random` not imported by renderer | `render.py` twice on `example/story` -> identical sha1 for all frames; 20 frames pixel-diff 0 vs the old CSV path (legacy `stage.scale`); `grep -n "random" core/render*.py` empty |
| 2. MVC teacher "Ustaani" | persona preset -> base plate -> 16 layers -> anchors -> manifest -> QA grid | contact grid approved; manifest validates; a 30 s English clip renders with lip-sync | Blind check: 3 people watch the 30 s clip and the same audio with character_1; new character is not rated worse on sync. Eye/mouth anchors within 5 px of a human click on head M. Total image-gen calls logged <= 15 |
| 3. Urdu + timeline editing | ElevenLabs timestamps -> visemes; override editor path (`tools/tl.py set --from 41 --to 54 eyes=worried_M`) | a code-switched Urdu/English 60 s clip renders; overrides survive regeneration | Viseme X coverage during silences >= 90% of silent frames (from alignment); `tl.py` edit then re-render changes only frames 41-54 (sha1 compare); re-running the generator keeps the override |
| 4. Full characters + student | 3 heads, 6 emotions, 27 mouths, 12 gestures for teacher; MVC student; 5 backgrounds | two-character scene (teacher asks, student answers) renders from one timeline | Contact grids approved; per-character calls <= 60; a 3-minute lesson renders in under 10 min on the laptop with the frame cache; `timeline.json` under 3k runs |

## 10. Five changes to Design-your-perfect-AI-Persona for synctoon-ready output

1. **"Export layer pack" mode** (new `POST /api/generate-layer-pack`): after the reference image, generate the base
   plate (front, T-pose, neutral face, flat green `#00FF00`, fixed 1920x1080, feet at y=1040; `imageConfig.aspectRatio
   "16:9"` is already set in `server.ts`), then the variant strips of section 3 in a fixed order, and return a zip
   with the naming convention of section 2. The wizard picks MVC or Full.
2. **Reference image input**: `generateContent` `parts` currently carry text only; add the reference image (and the
   base plate for later steps) as `inlineData` so every variant is an edit of the same identity, not a fresh sample.
   Also pass a mask image when the model version supports region edits.
3. **Presets and style lock**: a `preset` field in `AvatarConfig` (`taleemabad-teacher`, `taleemabad-student`) that
   pre-fills `artDirection`, `clothing`, `colorIdentity` and appends the flat-colour/clean-outline/no-shadow rules to
   the `systemInstruction`, so `masterPrompt` cannot drift into painterly renders that will not chroma-key.
4. **Server-side cut + anchors**: run the chroma-key and diff-landmarking in the Node server (sharp/canvas) or shell
   out to the Python tool, and include `anchors.json` and a draft `character.json` in the zip; return the QA contact
   grid as the result image in `ResultView` instead of only the reference image.
5. **Persist and reroll per layer**: store the `masterPrompt`, seeds and per-layer prompts with the character
   (`localStorage` now, a folder on disk in the Express server), and add a per-cell "regenerate" button on the
   contact grid so a bad viseme D is rerolled alone rather than the whole pack; log call counts per character.
