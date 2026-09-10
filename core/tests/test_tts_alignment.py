"""Runnable with `python -m pytest core/tests/test_tts_alignment.py` or
`python core/tests/test_tts_alignment.py` directly (from core/ or repo root)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from brain_requests.tts import alignment_to_gentle


def _fake_alignment(text):
    """Build a fake ElevenLabs per-character alignment: 0.05s per character."""
    characters = list(text)
    start = [round(i * 0.05, 2) for i in range(len(characters))]
    end = [round((i + 1) * 0.05, 2) for i in range(len(characters))]
    return {
        "characters": characters,
        "character_start_times_seconds": start,
        "character_end_times_seconds": end,
    }


def test_word_split_basic():
    text = "hi there"
    result = alignment_to_gentle(text, _fake_alignment(text))
    assert result["transcript"] == text
    words = result["words"]
    assert [w["word"] for w in words] == ["hi", "there"]


def test_word_boundaries():
    text = "hi there"
    result = alignment_to_gentle(text, _fake_alignment(text))
    words = result["words"]

    # "hi" = chars 0,1 -> start at char 0's start, end at char 1's end
    assert words[0]["start"] == 0.0
    assert words[0]["end"] == 0.10

    # "there" starts after the space (char index 3) through char index 7
    assert words[1]["start"] == 0.15
    assert words[1]["end"] == 0.40


def test_word_case_and_aligned_word_fields():
    text = "one two"
    result = alignment_to_gentle(text, _fake_alignment(text))
    for w in result["words"]:
        assert w["case"] == "success"
        assert w["alignedWord"] == w["word"]
        assert w["end"] > w["start"]


def test_multiple_spaces_do_not_produce_empty_words():
    text = "a  b"
    result = alignment_to_gentle(text, _fake_alignment(text))
    words = [w["word"] for w in result["words"]]
    assert words == ["a", "b"]


def test_punctuation_is_stripped_so_g2p_does_not_choke():
    # Regression: g2p_en phonemizes raw "," / "." tokens into ' ' / ',' pseudo-phonemes
    # that update_character_asset_name.py can't look up (KeyError) -- word/alignedWord
    # must come out clean even though the audio timing still covers the punctuation.
    text = "Sprout, was tiny."
    result = alignment_to_gentle(text, _fake_alignment(text))
    words = [w["word"] for w in result["words"]]
    assert words == ["Sprout", "was", "tiny"]
    for w in result["words"]:
        assert all(c.isalnum() for c in w["alignedWord"])


if __name__ == "__main__":
    test_word_split_basic()
    test_word_boundaries()
    test_word_case_and_aligned_word_fields()
    test_multiple_spaces_do_not_produce_empty_words()
    print("All tests passed.")
