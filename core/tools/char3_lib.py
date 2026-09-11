"""Shared helpers for the character_3 (Gemini plate + masked edits) build."""
import numpy as np
from PIL import Image, ImageFilter


def key_green(img, feather=1):
    """Chroma-key any 'green-dominant' pixel (handles off-#00FF00 greens and ground shadows).
    Returns RGBA with despilled edges."""
    import cv2
    a = np.asarray(img.convert("RGB")).astype(np.int16)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    hsv = cv2.cvtColor(a.astype(np.uint8), cv2.COLOR_RGB2HSV)  # H in 0..179
    h, s, v = hsv[..., 0].astype(int), hsv[..., 1].astype(int), hsv[..., 2].astype(int)
    green = (h > 32) & (h < 72) & (s > 45) & (v > 70)  # hue 64..144 deg; teal kameez is ~173 deg
    alpha = np.where(green, 0, 255).astype(np.uint8)
    al = Image.fromarray(alpha)
    # erode 1px to kill the green fringe, then feather
    al = al.filter(ImageFilter.MinFilter(3))
    if feather:
        al = al.filter(ImageFilter.GaussianBlur(feather))
    rgb = a.copy()
    # despill: on semi-transparent / edge pixels, clamp green to max(r,b)
    mx = np.maximum(r, b)
    spill = g > mx + 20
    rgb[..., 1] = np.where(spill, mx, g)
    out = Image.fromarray(rgb.astype(np.uint8), "RGB").convert("RGBA")
    out.putalpha(al)
    return out


def bbox(rgba, thresh=128):
    a = np.asarray(rgba.getchannel("A")) > thresh
    ys, xs = np.where(a)
    return (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)


def row_widths(rgba, thresh=128):
    a = np.asarray(rgba.getchannel("A")) > thresh
    return a.sum(axis=1)


def dark_blobs(rgba, box, thr=70):
    """Connected dark components inside box -> list of (cx, cy, w, h, area), by area desc."""
    import cv2
    x0, y0, x1, y1 = box
    crop = np.asarray(rgba.convert("RGB"))[y0:y1, x0:x1]
    gray = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY)
    m = (gray < thr).astype(np.uint8)
    n, lab, stats, cent = cv2.connectedComponentsWithStats(m)
    out = []
    for i in range(1, n):
        x, y, w, h, area = stats[i]
        out.append((x0 + cent[i][0], y0 + cent[i][1], w, h, area))
    return sorted(out, key=lambda t: -t[4])
