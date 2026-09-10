# synctoon rig manifest: `character.json` + `timeline.json`

Status: proposal (2026-09-10). Replaces `core/images/metadata/metadata.json`,
`core/utils/mouth_image.json`, `video_frames_info.csv`, `frameCreationInfo.json`
and the hardcoded tables in `core/utils/constants.py`.

## 1. What exists today, and what breaks

| File / code | What it stores | Problem observed |
|---|---|---|
| `metadata.json` (`character_1` → `background`/`body`/`eyes`/`mouth`) | absolute `position`+`size` per asset name | Eyes: 28 entries, 25 of them `{"size":[250,150],"position":[10,30]}` (3 one-off variants: `angry_2`-style overrides); keyed by emotion folder, not file (`CharacterManager.get_asset` line 85 sets `asset_name = asset_sub_type`). The 93x96 `happy_M.png` is stretched to 250x150 (aspect broken). `mouth` block contains 26 copy-pasted emotion keys (`angry`, `happy_2`...) that no code reads. Background: 28 of 32 entries identical; `body` 800x1080 is resized to 750x1080 (squashed). No head entry at all (`get_asset` returns `metadata=None` for head). |
| `CharacterManager.adding_eyes_and_mouth` :169, `adding_background` :195 | — | `mirror=True` hardcoded for mouth and for body. Flip is not data. |
| `CharacterManager.get_random_png_file_name` :21-32 | — | `random.choice` at render time for body/head/background. Every folder has exactly 1 PNG today, so it is accidentally deterministic; add a second `explain` pose and renders become non-reproducible. |
| `mouth_image.json` | ARPAbet (with stress digit) → `{happy, sad}` → filename | 69 keys x 2, 10 shapes `a_e, d_j_ch, f, l, m_b_close, o_big, o_small, oh, th, trans` (+`_h`/`_s`). `o_big`, `oh`, `trans` unreachable from the map; `K → a_e` and `N,R,T → th` are ad hoc. Emotion suffix baked into filename. |
| `frame_info_generator.py` | 15-column CSV, one row per frame (817 rows for a 34 s clip) | Blink sequence `["02","03","04"]` every 80 frames hardcoded (:58-59); rest mouth `m_b_close_h/_s` hardcoded (:141-144). Editing "frames 41-54 look angry" means editing 14 rows by hand. |
| `frame_generator.py` :44 | reads CSV | `bool(row["Blink"])` is `True` for the string `"False"` -> blink path always taken; this is why every `*_blink/` folder also contains `happy_L/M/R.png` copies (6 PNGs, not 3). |
| `frame_generator.py` :45-56, `frameCreationInfo.json` | cache key = fields concatenated with no separator (`character_1happyachieveMhappy_Mgreenhappym_b_close_h0`) | Ambiguous; `frame_key` maps every frame index to it, so the video step depends on a side file. |
| `constants.py` | int → name tables | `body_actions` has duplicates (1 and 9 both `achieve`) and gaps (26, 29); emotions/gestures are code, not data. |
| `add_phonemes.py` | g2p-en per word, frames split equally across phonemes | Gentle already returns timed phones (`output_fi.json` word 3: `m_B 0.05, eh_I 0.09, d_I 0.04, ow_E 0.23`). They are discarded. `output_fi.json` `phonemes_frame` is a dict, `distribute_frames` returns a list: schema drift between runs. |

Asset facts (character_1): head 359x293 RGBA (featureless yellow blob, 3 angles), eyes 93x96, mouth 375x154,
body 800x1080 (headless stick figure, 65 poses in 40 folders), background 1920x1080 RGB (32).
A "layer" is one transparent PNG that is pasted at a point; the head is a layer that receives eyes and mouth, the body is a layer that receives the head.

## 2. Proposal in one paragraph

One `character.json` per character folder, describing layers in **local coordinates**: every asset has a
`pivot` (a point inside its own PNG) and every "parent" layer has named `anchors`. Placement = put the child's
pivot on the parent's anchor, at scale 1 (all layers of a character are cut from one master sheet, so no per-asset
`size`). Head angle carries its own `eyes`/`mouth` anchors; a body pose carries a `head` anchor. A new body pose
needs one anchor, a new head angle needs two, and no eye/mouth coordinate is ever re-entered. Visemes use
Rhubarb's A-H+X. Emotions, gaze, gesture are tags. Rendering reads one `timeline.json` of runs. No randomness at
render time.

## 3. Folder layout

```
characters/<char_id>/
  character.json            # the rig
  head/  eyes/  mouth/  body/          # PNGs, flat; names free but conventional (see docs/TALEEMABAD_CHARACTER_PIPELINE.md)
scenes/<scene_id>/
  timeline.json             # per-video, editable source of truth
  audio.mp3  words.json     # aligner output kept for reference
backgrounds/<name>.png + backgrounds.json  # shared; not per character
```

## 4. Example `character.json` (character_1 migrated, abbreviated to 3 items per layer)

```json
{
  "schema": "synctoon-character/1",
  "id": "character_1",
  "display_name": "Hero",
  "canvas": {"width": 1920, "height": 1080, "fps": 24},
  "z_order": ["background", "body", "head", "eyes", "mouth"],
  "stage": {"anchor": [960, 1080], "body_pivot_hint": "feet-center", "scale": 0.9375, "flip": true,
            "zoom_point": [700, 400]},
  "layers": {
    "body": {
      "parent": "stage",
      "assets": {
        "explain/body15": {"file": "body/body15.png", "pivot": [400, 1080],
                           "anchors": {"head": [382, 162]}, "tags": {"gesture": "explain"}},
        "standing/body33": {"file": "body/body33.png", "pivot": [400, 1080],
                           "anchors": {"head": [372, 152]}, "tags": {"gesture": "standing"}},
        "achieve/body1":  {"file": "body/body1.png",  "pivot": [400, 1080],
                           "anchors": {"head": [382, 162]}, "tags": {"gesture": "achieve"}}
      }
    },
    "head": {
      "parent": "body", "attach": "head",
      "assets": {
        "M": {"file": "head/M.png", "pivot": [179, 146],
              "anchors": {"eyes": [135, 105], "mouth": [115, 227]}, "tags": {"angle": "M"}},
        "L": {"file": "head/L.png", "pivot": [179, 146],
              "anchors": {"eyes": [135, 105], "mouth": [115, 227]}, "tags": {"angle": "L"}},
        "R": {"file": "head/R.png", "pivot": [179, 146],
              "anchors": {"eyes": [135, 105], "mouth": [115, 227]}, "tags": {"angle": "R"}, "flip": false}
      }
    },
    "eyes": {
      "parent": "head", "attach": "eyes",
      "assets": {
        "happy_M":  {"file": "eyes/happy_M.png",  "pivot": [46, 48], "tags": {"emotion": "happy", "gaze": "M"}},
        "happy_L":  {"file": "eyes/happy_L.png",  "pivot": [46, 48], "tags": {"emotion": "happy", "gaze": "L"}},
        "blink_2":  {"file": "eyes/happy_blink/03.png", "pivot": [46, 48], "tags": {"emotion": "happy", "blink": 2}}
      }
    },
    "mouth": {
      "parent": "head", "attach": "mouth", "flip": true,
      "assets": {
        "A_happy": {"file": "mouth/happy/m_b_close_h.png", "pivot": [187, 77], "tags": {"viseme": "A", "emotion": "happy"}},
        "C_happy": {"file": "mouth/happy/a_e_h.png",       "pivot": [187, 77], "tags": {"viseme": "C", "emotion": "happy"}},
        "X_sad":   {"file": "mouth/sad/trans_s.png",       "pivot": [187, 77], "tags": {"viseme": "X", "emotion": "sad"}}
      }
    }
  },
  "defaults": {"body": "standing/body33", "head": "M", "eyes": {"emotion": "happy", "gaze": "M"},
               "mouth": {"emotion": "happy"}, "rest_viseme": "X"},
  "emotion_sets": {"happy": ["happy", "content", "sarcasm", "crazy", "evil_laugh", "lust", "silly"],
                   "sad": ["sad", "angry", "bore", "glare", "worried", "shock", "spoked"]},
  "blink": {"sequence": ["blink_1", "blink_2", "blink_3"], "every_frames": 80, "hold": 1},
  "aliases": {"mouth": {"m_b_close": "A", "d_j_ch": "B", "th": "B", "a_e": "C", "o_big": "D",
                        "oh": "E", "o_small": "F", "f": "G", "l": "H", "trans": "X"}}
}
```

Placement rule (the whole renderer): `pos(child) = pos(parent) + parent.anchors[attach] - child.pivot`, scaled
by `stage.scale` only. `flip` is data (per layer or per asset), applied around the pivot before pasting. Today's
`mirror=True` for mouth becomes `layers.mouth.flip: true` and can be turned off per character.

Legacy mapping used above: body head-anchor = old `body.position + size/2` (285x255 head pasted at (240,35) ->
anchor (382,162)); head pivot = head centre; eyes anchor = old `eyes.position + size/2` in head space;
`stage.scale` = 750/800 (the old squash, kept only so the migrated character_1 renders identically; new
characters use 1.0 and are authored at canvas scale).

## 5. Viseme set

| Candidate | Count | Verdict |
|---|---|---|
| Preston Blair | 10 (A-I, L, M-B-P, O, E, F-V, W-Q, TH, rest...) | Classic for hand animation, but the TH/W-Q/L splits are more mouths to draw for little on-screen difference at 24 fps with 2-4 frames per phone. |
| Papagayo | uses Preston Blair set by default; adds its own "Fleming & Dobbs" | Tool-specific UI format (`.pgo`), not a standard on its own. |
| **Rhubarb Lip Sync A-H + X** | 9 | Chosen. Fewest shapes that still read clearly; documented mapping from phones; Rhubarb itself can run on the WAV in phonetic mode (no transcript), which is the escape hatch for Urdu audio; G and H are optional in Rhubarb (fall back to B) so a minimum character needs 7 mouths. |

ARPAbet (g2p-en output; strip stress digits with `re.sub(r"\d","",p)`) → viseme:

| Viseme | Meaning | ARPAbet | Old filename (alias) |
|---|---|---|---|
| A | closed, pressed | P B M | `m_b_close` |
| B | slightly open, teeth | CH D DH G HH JH K N NG S SH T TH Y Z ZH, IY IH | `d_j_ch`, `th` |
| C | open | EH AE AH EY AY | `a_e` |
| D | wide open | AA AW | `o_big` (verify visually; 50x50 in old metadata is suspicious) else fall back to C |
| E | slightly rounded | AO ER OY | `oh` |
| F | puckered | UW UH OW W | `o_small` |
| G | teeth on lip | F V | `f` |
| H | tongue up | L | `l` |
| X | rest / silence | sil, sp, pauses between words | `trans` |

Gentle phones (`m_B`, `eh_I`, `ow_E` in `output_fi.json`) are the same set lower-cased with a position
suffix: `p.split("_")[0].upper()` then the table above. Use Gentle's `duration` for frame counts instead of the
equal split in `add_phonemes.distribute_frames`; that is where the lip-sync looks "floaty" today.
Emotion is a separate tag (`emotion: happy|sad|neutral`); the renderer selects `viseme AND emotion`, falling back
to `neutral` then to any asset with that viseme. `emotion_sets` replaces `happy_mouth` in
`update_character_asset_name.py` :8.

## 6. Tags instead of folder names

`constants.emotions`, `body_actions`, `screen_mode` become derived: `available("body","gesture")` = distinct
tag values in the manifest. The LLM prompt in `core.py` (via `brain_requests`) should be built from that list, so
a character with 3 gestures never gets asked for `kung_fu`. Intensity `_2` becomes `"intensity": 2` tag. Folder
paths in `file` are free; nothing in code joins `asset_type/asset_sub_type/name` any more
(`CharacterManager.get_character_asset_path`, `get_eyes_blinking_asset_path` go away).

## 7. Timeline: the single editable source of truth

`scenes/<id>/timeline.json`, one object, `runs` are contiguous non-overlapping base state, `overrides` are sparse
patches applied on top in list order. Frame `f` state = base run containing `f`, then each override containing `f`.

```json
{"schema": "synctoon-timeline/1", "character": "character_1", "fps": 24, "frames": 817,
 "audio": "audio.mp3", "seed": 20260910, "generator": "core.py@<git-sha>",
 "runs": [
  {"from": 0,  "to": 19,  "layers": {"background": "white", "body": "standing/body33", "head": "M", "eyes": "happy_M", "mouth": "X"}, "note": "lead-in"},
  {"from": 20, "to": 22,  "layers": {"body": "joy/body24", "mouth": "A"}, "word": "meadow", "phone": "M"},
  {"from": 23, "to": 25,  "layers": {"mouth": "C"}, "phone": "EH1"},
  {"from": 26, "to": 27,  "layers": {"mouth": "B"}, "phone": "D"},
  {"from": 28, "to": 30,  "layers": {"mouth": "F"}, "phone": "OW2"},
  {"from": 31, "to": 40,  "layers": {"mouth": "X"}},
  {"from": 41, "to": 54,  "layers": {"eyes": "angry_M", "head": "L", "mouth": "C", "mouth_emotion": "sad"}, "word": "hungry"},
  {"from": 55, "to": 57,  "layers": {"mouth": "B"}, "phone": "NG"},
  {"from": 58, "to": 120, "layers": {"head": "M", "eyes": "happy_M", "mouth": "X", "body": "explain/body15"}},
  {"from": 121,"to": 816, "layers": {"background": "classroom", "body": "standing/body33"}}
 ],
 "overrides": [
  {"from": 80,  "to": 82,  "seq": {"eyes": ["blink_1", "blink_2", "blink_3"]}, "kind": "blink"},
  {"from": 160, "to": 162, "seq": {"eyes": ["blink_1", "blink_2", "blink_3"]}, "kind": "blink"},
  {"from": 300, "to": 420, "camera": {"zoom": 2.0, "at": "head", "ease": "in-out", "ramp": 12}, "kind": "zoom"},
  {"from": 41,  "to": 54,  "layers": {"eyes": "worried_M"}, "by": "kamal", "note": "angry too strong here"}
 ]}
```

Rules: a run only lists layers that change (inherit the rest from the previous run: 10 lines instead of 55
identical CSV rows). `seq` cycles a list over the range, one entry per frame (blink = one line, not three rows
x N). `camera.zoom` replaces the CSV `Zoom` int and `zoom_at` (`CharacterManager.zoom_at`); `at: "head"` resolves
to the head's placed pivot so zoom follows the character instead of a per-background `zoom_point`.
`mouth: "C"` is a viseme, resolved with the current `mouth_emotion` at render time via tags; `mouth: "@file:x.png"`
pins a literal file when a human insists.

Why runs beat one row per frame: (1) a human edit is "frames 41-54" not 14 rows; (2) an LLM edit fits in a
prompt (a 10-minute video is ~14k CSV rows, ~1-2k runs); (3) diffs in git are readable; (4) `overrides` keep
hand edits separate from regenerated base runs, so re-running the aligner does not destroy them; (5) validation is
trivial: runs must tile `0..frames-1`, `overrides` may not reference unknown asset ids; (6) the cache key becomes
`sha1(canonical_json(resolved_frame_state))`, which removes `frameCreationInfo.json` entirely.

"Every frame is controllable" becomes literally true: any frame `f` can be pinned with an override
`{"from": f, "to": f, "layers": {...}}` and the rest of the video is untouched.

## 8. Determinism

- `generate_timeline(words, character, seed)` is the only place `random.Random(seed)` is used (body variant when
  a gesture has several PNGs, blink jitter). The chosen asset ids are written into `runs`; `seed` is stored in the
  header so regeneration is reproducible.
- `render(timeline, character)` imports no `random`. Given the same two files and the same PNG bytes, the output
  frames are byte-identical. Test: render twice, compare sha1 of every frame.
- Frame cache: `frames/<sha1>.png`; a frame index → sha1 list is derived in memory, never persisted.

## 9. Migration outline (`tools/migrate_metadata.py`, stdlib + PIL)

```python
old = json.load(open("core/images/metadata/metadata.json"))["character_1"]
mouth_map = json.load(open("core/utils/mouth_image.json"))
ALIAS = {"m_b_close":"A","d_j_ch":"B","th":"B","a_e":"C","o_big":"D","oh":"E","o_small":"F","f":"G","l":"H","trans":"X"}
rig = {"schema":"synctoon-character/1","id":"character_1","canvas":{...},"z_order":[...],
       "stage":{"anchor":[250+375,160+1080],"scale":750/800,"flip":True,"zoom_point":[700,400]},"layers":{}}
def centre(p, s): return [p[0]+s[0]//2, p[1]+s[1]//2]
body = {}
for folder in Path("body").iterdir():                      # gesture = folder name -> tag
    for png in folder.glob("*.png"):
        m = old["body"][png.stem]; w,h = Image.open(png).size
        body[f"{folder.name}/{png.stem}"] = {"file":f"body/{png.name}","pivot":[w//2,h],
            "anchors":{"head":centre(m["position"],m["size"])},"tags":{"gesture":folder.name}}
eye_m = old["eyes"]["happy"]; mouth_m = old["mouth"]["a_e_h"]   # 25/28 eye entries identical; 3 outliers become per-asset overrides
head = {a:{"file":f"head/{a}.png","pivot":[359//2,293//2],
           "anchors":{"eyes":centre(eye_m["position"],eye_m["size"]),"mouth":centre(mouth_m["position"],mouth_m["size"])},
           "tags":{"angle":a}} for a in ("L","M","R")}
eyes = {}
for emo_dir in Path("eyes").iterdir():                     # happy, happy_2, ... ; *_blink subfolder
    emo, inten = re.match(r"(.+?)(?:_(\d))?$", emo_dir.name).groups()
    for png in emo_dir.glob("*.png"):                      # happy_L/M/R
        eyes[png.stem] = {"file":..., "pivot":[46,48], "tags":{"emotion":emo,"gaze":png.stem[-1],"intensity":int(inten or 1)}}
    for i,png in enumerate(sorted((emo_dir/f"{emo_dir.name}_blink").glob("0*.png")),1):   # 02,03,04 only
        eyes[f"{emo_dir.name}_blink_{i}"] = {"file":..., "pivot":[46,48], "tags":{"emotion":emo,"blink":i}}
mouth = {}
for png in Path("mouth").rglob("*.png"):                   # a_e_h.png -> shape a_e, emotion h
    shape, e = png.stem.rsplit("_",1); vis = ALIAS[shape]
    mouth[f"{vis}_{ {'h':'happy','s':'sad'}[e] }"] = {"file":..., "pivot":[187,77], "tags":{"viseme":vis,"emotion":{"h":"happy","s":"sad"}[e]}}
rig["layers"] = {"body":{"parent":"stage","assets":body}, "head":{"parent":"body","attach":"head","assets":head},
                 "eyes":{"parent":"head","attach":"eyes","assets":eyes}, "mouth":{"parent":"head","attach":"mouth","flip":True,"assets":mouth}}
rig["aliases"] = {"mouth": ALIAS, "arpabet": {re.sub(r"\d","",k): ALIAS[v["happy"].rsplit("_",1)[0]] for k,v in mouth_map.items()}}
json.dump(rig, open("characters/character_1/character.json","w"), indent=1)
# then: render 20 frames from an old CSV via both paths, assert pixel-diff == 0 (accepting the legacy stage.scale).
```

Note the anchor for eyes uses the 250x150 target box centre, not the 93x96 source, so the migrated eyes land in
the same place but are no longer stretched; expect them to look smaller. Regenerate eye PNGs at 250x150 once
(pipeline doc, Phase 1) or set `"scale": [2.69, 1.56]` on the eyes layer as a temporary, explicit distortion.

## 10. Alternatives considered

| Option | One-line verdict |
|---|---|
| Keep `metadata.json` + `mouth_image.json` + CSV | Zero migration, but absolute coordinates per asset and the CSV are exactly what makes new characters and frame edits expensive; also 3 files must agree. |
| SQLite | Great for the frame cache index, wrong for assets: not diffable, not hand-editable, needs a schema tool for LLM edits; nothing here is relational beyond parent/child. |
| Spine / DragonBones JSON | Real skeletal rigs with bones, slots, attachments; heavy runtime, editors are the point, and synctoon has no bones, only swaps. Borrow the vocabulary (`slot`, `attachment`, `pivot`), not the format. |
| Lottie | Vector/After-Effects export format; raster layer swaps are possible via image assets but timeline semantics are keyframe-based and the file is write-only for humans. |
| Adobe Character Animator puppet (.puppet) | Closed, layer-name-driven (`+Mouth`, `Ah`, `D`, `Ee`...), needs Adobe; its layer naming idea is exactly our tag idea, so steal the naming, not the tool. |
| Live2D (.moc3/.model3.json) | Mesh deformation, proprietary runtime and editor; overkill for 2-4 frame swaps and expensive. |
| **Plain JSON manifest + runs timeline (this doc)** | stdlib `json`, two files per character/scene, readable diffs, editable by human or LLM, validator is 40 lines with `jsonschema` (already in `requirements.txt`). |

## 11. JSON Schema sketch (`schemas/character.schema.json`)

```
schema: string (const "synctoon-character/1")      id: string       display_name: string?
canvas: {width:int, height:int, fps:int}
z_order: string[]                                   # layer names, back to front
stage: {anchor:[int,int], scale:number, flip:bool, zoom_point:[int,int]?}
layers: map<layerName, Layer>
  Layer: {parent: "stage"|layerName, attach: string? (required unless parent=="stage"),
          flip: bool?, scale: number|[number,number]?, assets: map<assetId, Asset>}
  Asset: {file: string (relative path), pivot:[int,int], anchors: map<string,[int,int]>?,
          tags: map<string, string|int|bool>, flip: bool?}
defaults: {body:assetId, head:assetId, eyes:{emotion,gaze}, mouth:{emotion}, rest_viseme: "X"}
emotion_sets: map<string, string[]>?
blink: {sequence: assetId[] | tag-pattern, every_frames:int, hold:int}?
aliases: {mouth: map<oldShape, viseme>, arpabet: map<phone, viseme>}?
additionalProperties: false at every level; assetId pattern ^[A-Za-z0-9_./-]+$
```

Timeline schema: `runs[]` `{from:int, to:int, layers: map<layer, assetId|viseme|"@file:..">, word?, phone?, note?}`;
`overrides[]` same plus `seq: map<layer, assetId[]>`, `camera: {zoom:number, at: "head"|[x,y], ease?, ramp?}`,
`kind?`, `by?`. Validator asserts runs tile `[0, frames)` and every referenced id exists in `character.json`.
