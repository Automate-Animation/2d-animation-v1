import json
import logging
from pathlib import Path

from utils.constants import emotions, body_actions, screen_mode


LOGGER = logging.getLogger(__name__)


def _load_mouth_image_mapping():
    mouth_image_path = Path(__file__).resolve().parent / "mouth_image.json"
    try:
        with mouth_image_path.open("r", encoding="utf-8") as json_file:
            return json.load(json_file)
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"Unable to locate mouth image configuration file at {mouth_image_path}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Failed to parse mouth image configuration file at {mouth_image_path}: {exc}"
        ) from exc


response_json = _load_mouth_image_mapping()


happy_mouth = ["happy", "content", "sarcasm", "crazy", "evil_laugh", "lust", "silly"]


def update_assets(data):
    words = data.get("words", [])
    LOGGER.debug("Updating assets for %d word(s)", len(words))
    for each_data in words:
        # emotion
        if int(each_data["intensity"]) == 2:
            each_data["emotion_name"] = emotions.get(each_data["emotion"]) + "_2"
        else:
            each_data["emotion_name"] = emotions.get(each_data["emotion"])

        # character
        each_data["character_name"] = "character_" + str(each_data["character"])

        # background
        each_data["background_name"] = screen_mode.get(int(each_data["screen_mode"]))[
            "name"
        ]

        # body
        each_data["body_name"] = body_actions.get(int(each_data["body_action"]))

        # mouth
        if each_data["emotion_name"] in happy_mouth:
            emotion = "happy"
        else:
            emotion = "sad"
        phonemes_frame_details = []
        for phoneme in each_data["phonemes_frame"]:
            detail = {}
            detail["phoneme"] = phoneme["name"]
            detail["frame"] = phoneme["frames"]
            detail["emotion"] = emotion
            detail["mouth_name"] = response_json[phoneme["name"]][emotion]
            phonemes_frame_details.append(detail)
        each_data["phonemes_frame_details"] = phonemes_frame_details
    return data
