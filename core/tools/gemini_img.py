#!/usr/bin/env python3
"""Minimal Gemini image generate/edit helper (REST, no SDK). Counts every call in build/char3/calls.log.

    from tools.gemini_img import gen
    gen("prompt", "out.png")                       # text -> image
    gen("prompt", "out.png", images=["plate.png"]) # image edit (source PNGs passed as inlineData)

Key: GEMINI_API_KEY env or /home/oye/Documents/free_work/Design-your-perfect-AI-Persona/.env (never printed).
"""
import base64
import json
import os
import sys
import time

import requests

ENV_FILE = "/home/oye/Documents/free_work/Design-your-perfect-AI-Persona/.env"
DEFAULT_MODEL = "gemini-2.5-flash-image"
LOG = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "build", "char3", "calls.log")


def _key():
    k = os.environ.get("GEMINI_API_KEY")
    if k:
        return k
    with open(ENV_FILE) as f:
        for line in f:
            if line.startswith("GEMINI_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("GEMINI_API_KEY not found")


def _log(model, out, ok, note=""):
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a") as f:
        f.write(f"{time.strftime('%H:%M:%S')}\t{model}\t{'ok' if ok else 'FAIL'}\t{out}\t{note}\n")


def calls():
    return sum(1 for _ in open(LOG)) if os.path.exists(LOG) else 0


def gen(prompt, out, images=(), model=DEFAULT_MODEL, retries=2, aspect=None):
    parts = []
    for p in images:
        with open(p, "rb") as f:
            parts.append({"inlineData": {"mimeType": "image/png", "data": base64.b64encode(f.read()).decode()}})
    parts.append({"text": prompt})
    body = {"contents": [{"parts": parts}], "generationConfig": {"responseModalities": ["IMAGE"]}}
    if aspect:
        body["generationConfig"]["imageConfig"] = {"aspectRatio": aspect}
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    last = None
    for attempt in range(retries + 1):
        r = requests.post(url, params={"key": _key()}, json=body, timeout=180)
        if r.status_code != 200:
            last = f"http {r.status_code}: {r.text[:200]}"
            _log(model, out, False, last)
            time.sleep(3 * (attempt + 1))
            continue
        data = r.json()
        for part in data.get("candidates", [{}])[0].get("content", {}).get("parts", []):
            if "inlineData" in part:
                os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
                with open(out, "wb") as f:
                    f.write(base64.b64decode(part["inlineData"]["data"]))
                _log(model, out, True)
                return out
        last = "no image part: " + json.dumps(data)[:200]
        _log(model, out, False, last)
    raise RuntimeError(f"gemini failed for {out}: {last}")


if __name__ == "__main__":
    # usage: gemini_img.py out.png "prompt" [source.png ...]
    gen(sys.argv[2], sys.argv[1], images=sys.argv[3:])
    print("calls so far:", calls())
