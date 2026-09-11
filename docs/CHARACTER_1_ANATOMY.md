# How character_1 is built — and why it animates better than character_2/3

Investigation of Kamal's original rig (`core/images/characters/character_1`), 2026-09-11.
Everything below was read from the PNGs and `metadata.json`, not assumed.

## 1. Every part is an isolated, transparent sprite — no skin, no background

| Part | What the PNG contains | What it does NOT contain |
|---|---|---|
| `head/{L,M,R}` | a plain yellow oval, 359x293 | no eyes, no mouth, no nose |
| `eyes/<emotion>/<emotion>_{L,M,R}` | eyebrows + eyeballs + pupils, line art | no skin |
| `eyes/<emotion>/<emotion>_blink/{02,03,04}` | eyelid shapes only (02 lids, 03 closed, 04 half) | no skin |
| `mouth/{happy,sad}/<viseme>_{h,s}` | the mouth shape only (lips/teeth/tongue), tight-cropped | no skin, no nose |
| `body/<action>/bodyN` | headless stick body in a pose | no head |

Consequence: any sprite can be pasted on any head at any position, mirrored, or resized and
**there is never a seam**, because there is no skin rectangle to mismatch.
character_3's mouth sprites are skin rectangles with the nose inside them (see
`build/qa` sheets and `mouth/happy/*.png`): pasted with `mirror=True` they flip a lit,
asymmetric skin patch, so the mouth lands off-centre and the skin tone shifts.
That is the "mouth on one side" defect. Same for its eye patches.

## 2. Mouths: 20 distinct drawings, each with its own box

`metadata.json["character_1"]["mouth"]` is keyed per viseme FILE, and the boxes differ:

| Viseme | happy size / position | note |
|---|---|---|
| a_e, d_j_ch, f, l, th | 110x55 @ (60,200) | wide shapes |
| trans | 110x45 @ (60,200) | in-between shape |
| m_b_close | 110x15 @ (60,220) | a thin closed line, lower |
| o_big, oh | 50x50 @ (80,200) | round, centred |
| o_small | 40x40 @ (80,200) | smaller round |

Sad versions are separate drawings (flatter, lower corners), with 110x45 boxes.
So the mouth changes SHAPE AND SIZE per sound, the way a lip-sync chart does.
character_2 used one 110x55 box for all 20; character_3 used one fixed cut box for all 20.
Both lose the size change, which is half of what makes lip-sync read.

`mouth_image.json` maps 70 ARPAbet phonemes → viseme: a_e 34, o_small 15, d_j_ch 10,
th 5, m_b_close 3, f 2, l 1 (o_big, oh, trans are never produced by the map — they exist
for hand edits).

## 3. Eyes: emotion is the drawing, direction is the pupil, blink is 3 lid frames

- Each emotion is a different eye+eyebrow drawing (sad = drooping lids, angry = heavy brow,
  shock = tall ovals, bore = half lids, glare = slits). `_2` folders are stronger versions.
- L/M/R differ only by pupil position inside the same eyeball. One drawing, three pupils.
- Blink = `02` (upper lids only), `03` (closed), `04` (half open, lower lids drawn).
  The CSV emits three consecutive rows 02,03,04 at blink time.
- Canvas sizes differ per emotion (236x182, 219x159, 236x121...) but they all share one box
  (250x150 @ (10,30)) — the drawing itself positions the eyes inside its canvas.

## 4. Head turn is faked by the eyes, not by the head

`head/L`, `head/M`, `head/R` are three near-identical ovals. The turn is carried by the
eye sprite's pupil offset and by which body pose is used. That is why it never breaks:
nothing has to be re-cut when the head "turns".

## 5. Bodies: 65 poses, each with its own head anchor

`body/` has 65 headless stick drawings mapped into 39 action folders. `metadata["body"]`
is keyed per body file with its own head `position` and `size` (e.g. body1 → (240,35),
body9 → (240,25)), so the head follows the pose (leaning, crouching, jumping).
The body is pasted with `mirror=True` — Kamal drew once and flips at paste time; because the
head is a blank oval and the face sprites are symmetric-ish line art, the flip is free.

## 6. What the render pipeline actually needs from a character (the contract)

1. Transparent sprites per part, tight-cropped, consistent line weight and palette.
2. A blank head (features removed) so eyes/mouth are the only face detail.
3. Per-viseme mouth boxes (size + position) — 10 shapes x 2 moods.
4. Per-emotion eye drawings with 3 pupil offsets and 3 lid frames.
5. Headless bodies with a per-body head anchor.
6. Everything at one scale, so `metadata.size == intended paste size` and nothing distorts.

## 7. Why character_2 and character_3 fell short

| | character_1 (Kamal) | character_2 (vector) | character_3 (Gemini) |
|---|---|---|---|
| mouth sprite | mouth only, transparent | mouth only, but crude | skin rectangle incl. nose |
| mouth box per viseme | yes (5 different boxes) | no (one box) | no (one box) |
| eyes | expressive drawings | plain ovals | skin rectangles incl. brows |
| blink frames | 3 drawn lid shapes | 3 procedural | closed/half edits, skin patches |
| body poses | 65 expressive, per-body anchor | 39 stiff IK tubes | 17 edits, one anchor |
| seams | none | none | visible on turned heads and mouths |
| art quality | strong cartoon | plain | good plate, ruined by the cutting |

The Gemini route produced good ART but the wrong KIND of sprite. The fix is not more
image calls; it is generating parts the way Kamal drew them: isolated, transparent, per-viseme.
