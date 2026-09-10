"""ElevenLabs TTS + word-timestamp synthesis.

Converts ElevenLabs' character-level alignment into the Gentle-shaped dict the rest
of the pipeline (add_phonemes.py, frame_info_generator.py) already expects:
{"transcript": text, "words": [{"word","alignedWord","case","start","end",
"startOffset","endOffset"}]}.

# ponytail: word split is whitespace-only apart from stripping leading/trailing
# punctuation (matching what Gentle's own "word"/"alignedWord" fields look like) —
# g2p_en chokes on a raw "," or "." token (add_phonemes.py -> update_character_asset_name.py
# KeyError), so punctuation has to go before those consume it. Interior punctuation
# (apostrophes etc.) is left alone. Upgrade to a real tokenizer if that ever matters.
"""
import base64
import json
import os
import re

import requests

from utils.env import load_env

load_env()

DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"
DEFAULT_MODEL_ID = "eleven_multilingual_v2"


def _chars_to_words(text, characters, char_start, char_end):
    """Split alignment into words on whitespace, using each word's first/last char times."""
    words = []
    word_chars = []
    word_start = None
    offset = 0  # running position in `text` for startOffset/endOffset

    def flush(end_offset):
        if not word_chars:
            return
        raw_text = "".join(c for c, _, _ in word_chars)
        word_text = re.sub(r"^[^\w]+|[^\w]+$", "", raw_text)
        if not word_text:
            return  # token was pure punctuation (e.g. a lone "-") -- nothing to phonemize
        w_start = word_chars[0][1]
        w_end = word_chars[-1][2]
        words.append(
            {
                "word": word_text,
                "alignedWord": word_text,
                "case": "success",
                "start": w_start,
                "end": w_end,
                "startOffset": end_offset - len(raw_text),
                "endOffset": end_offset,
            }
        )

    for i, ch in enumerate(characters):
        if ch.isspace():
            flush(offset)
            word_chars = []
        else:
            word_chars.append((ch, char_start[i], char_end[i]))
        offset += 1
    flush(offset)

    return words


def alignment_to_gentle(text, alignment):
    """alignment: ElevenLabs {"characters", "character_start_times_seconds",
    "character_end_times_seconds"} -> Gentle-shaped {"transcript","words"}."""
    words = _chars_to_words(
        text,
        alignment["characters"],
        alignment["character_start_times_seconds"],
        alignment["character_end_times_seconds"],
    )
    return {"transcript": text, "words": words}


def synthesize(text, out_mp3, voice_id=None, model_id=None) -> dict:
    """Synthesize `text` via ElevenLabs, write mp3 to out_mp3, write alignment JSON
    next to it, and return the Gentle-shaped alignment dict."""
    voice_id = voice_id or os.environ.get("ELEVENLABS_VOICE_ID", DEFAULT_VOICE_ID)
    model_id = model_id or os.environ.get("ELEVENLABS_MODEL_ID", DEFAULT_MODEL_ID)
    api_key = os.environ["ELEVENLABS_API_KEY"]

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps"
    resp = requests.post(
        url,
        headers={"xi-api-key": api_key, "Content-Type": "application/json"},
        json={"text": text, "model_id": model_id},
        timeout=180,
    )
    resp.raise_for_status()
    payload = resp.json()

    audio_bytes = base64.b64decode(payload["audio_base64"])
    os.makedirs(os.path.dirname(os.path.abspath(out_mp3)), exist_ok=True)
    with open(out_mp3, "wb") as f:
        f.write(audio_bytes)

    gentle_shaped = alignment_to_gentle(text, payload["alignment"])

    alignment_path = os.path.splitext(out_mp3)[0] + ".alignment.json"
    with open(alignment_path, "w") as f:
        json.dump(gentle_shaped, f, indent=2)

    return gentle_shaped
