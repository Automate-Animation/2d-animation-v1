#!/usr/bin/env python3
"""Robust per-image chroma key for character_4 sources. Gemini did not return pure #00FF00 --
the actual background came back a muted olive-green (~hsv 94deg/47%/73%) and the ground-shadow
under the reference's feet is a darker version of the SAME hue, not a different colour. Rather
than hardcode one key colour (char3_lib.key_green's fixed hue-band 32-72 in OpenCV's 0-179 scale
happens to cover this muted green too, verified on reference.png), sample each image's own corner
colour and key by HUE DISTANCE from that sample so a different muted-green batch would still work,
then do one extra erode pass + despill so no green fringe survives on tight-cropped edges (this is
exactly the seam-causing mistake character_3 made, just at the fringe-pixel level instead of the
whole-sprite level).
"""
import cv2
import numpy as np
from PIL import Image, ImageFilter


def sample_bg_hue(img_rgb, corner=24):
    """Median hue/sat/val of the four corners (skips any non-background stray anti-alias pixel)."""
    a = np.asarray(img_rgb)
    h, w = a.shape[:2]
    patches = [a[:corner, :corner], a[:corner, w - corner:], a[h - corner:, :corner], a[h - corner:, w - corner:]]
    stack = np.concatenate([p.reshape(-1, 3) for p in patches], axis=0)
    hsv = cv2.cvtColor(stack.reshape(1, -1, 3).astype(np.uint8), cv2.COLOR_RGB2HSV)[0]
    return tuple(np.median(hsv, axis=0))


def _flood_from_border(mask_keep, seed):
    """Flood-fill: grow `seed` (bool array, True=background so far) into any 4-connected
    neighbour also in mask_keep (bool array, True=candidate-background pixel). Returns the
    full connected background mask. Pure numpy/cv2, no scipy dependency."""
    seed_u8 = (seed & mask_keep).astype(np.uint8) * 255
    # cv2 floodFill needs a single seed point per call; instead use connectedComponents on
    # mask_keep, then keep every component that touches the original seed.
    n, lab = cv2.connectedComponents(mask_keep.astype(np.uint8))
    touched = set(np.unique(lab[seed & mask_keep]))
    touched.discard(0)
    out = np.isin(lab, list(touched)) if touched else np.zeros_like(mask_keep)
    return out


def key_green_adaptive(pil_img, feather=1, extra_erode=1, strip_white_halo=True):
    """Chroma-key using the IMAGE'S OWN sampled background hue (not a fixed #00FF00 assumption),
    with hue-distance thresholding so it also catches the darker-shade ground shadow, then an
    extra erosion pass + stronger despill to kill green fringe on tight-cropped sticker edges.

    Gemini also returned some stickers with a WHITE sticker-outline halo around the actual part
    (verified by direct inspection: mouth_o_big_h, mouth_d_j_ch_h, eyes_sad, etc.) -- plain
    green-hue keying leaves that halo fully opaque since white has near-zero saturation, not a
    green hue. Fix: after green-keying, flood-fill from the already-transparent border through
    any near-white/low-saturation pixel (the halo is always CONNECTED to the green background,
    never floating inside the character art) and key that too."""
    rgb = pil_img.convert("RGB")
    a = np.asarray(rgb).astype(np.int16)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    hsv = cv2.cvtColor(a.astype(np.uint8), cv2.COLOR_RGB2HSV)
    h, s, v = hsv[..., 0].astype(int), hsv[..., 1].astype(int), hsv[..., 2].astype(int)
    bh, bs, bv = sample_bg_hue(rgb)
    # hue distance on a circular 0-179 scale, generous tolerance so it also keys the darker
    # (lower-v) ground-shadow patch, which shares the background's hue
    hue_dist = np.minimum(np.abs(h - bh), 180 - np.abs(h - bh))
    green = (hue_dist < 16) & (s > 20) & (v > 25)

    bg = green.copy()
    if strip_white_halo:
        near_white = (s < 35) & (v > 170)  # low-sat, bright -- the sticker-outline halo colour
        candidate = green | near_white
        border = np.zeros_like(green)
        border[0, :] = border[-1, :] = border[:, 0] = border[:, -1] = True
        bg = _flood_from_border(candidate, border | green)

    alpha = np.where(bg, 0, 255).astype(np.uint8)
    al = Image.fromarray(alpha)
    al = al.filter(ImageFilter.MinFilter(3))
    if extra_erode:
        al = al.filter(ImageFilter.MinFilter(3))
    if feather:
        al = al.filter(ImageFilter.GaussianBlur(feather))
    rgb_arr = a.copy()
    # despill: pull green channel toward max(r,b) on ANY pixel whose hue is still green-ish
    # (not just fully-keyed ones) -- kills the thin green fringe on tight-cropped edges
    mx = np.maximum(r, b)
    fringe = hue_dist < 30
    rgb_arr[..., 1] = np.where(fringe, np.minimum(g, mx), g)
    out = Image.fromarray(rgb_arr.astype(np.uint8), "RGB").convert("RGBA")
    out.putalpha(al)
    return out


def edge_hue_check(rgba, band=2):
    """Returns mean hue of the alpha-edge ring (partially-transparent pixels) -- a green mean
    there means fringe survived. Used as a self-check after keying, not just eyeballing sheets."""
    a = np.asarray(rgba.getchannel("A"))
    edge = (a > 10) & (a < 245)
    if edge.sum() < 10:
        return None
    rgb = np.asarray(rgba.convert("RGB"))
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    return float(np.median(hsv[..., 0][edge]))
