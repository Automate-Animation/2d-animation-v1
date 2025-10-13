import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Optional

from brain_requests.speach_aligner import TranscriptionService
from brain_requests.text_aligner import TextAnalyzer
from brain_requests.utils import update_values
from utils.add_phonemes import add_phonemes
from utils.constants import body_actions, characters, emotions, screen_mode
from utils.frame_info_generator import video_frames_info
from utils.update_character_asset_name import update_assets


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_TRANSCRIPT_PATH = BASE_DIR.parent / "example" / "story" / "breakup.txt"
DEFAULT_AUDIO_PATH = BASE_DIR.parent / "example" / "story" / "breakup.mp3"
DEFAULT_SERVICE_URL = "http://localhost:49153/transcriptions?async=false"


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments for configuring the pipeline."""

    parser = argparse.ArgumentParser(
        description="Generate Synctoon animation metadata from transcript and audio."
    )
    parser.add_argument(
        "--transcript",
        help=(
            "Path to the transcript text file. Overrides the SYNCTOON_TRANSCRIPT_PATH "
            "environment variable."
        ),
    )
    parser.add_argument(
        "--audio",
        help=(
            "Path to the audio file. Overrides the SYNCTOON_AUDIO_PATH environment "
            "variable."
        ),
    )
    parser.add_argument(
        "--api-key",
        help=(
            "Google API key used by the text analyzer. Overrides the GOOGLE_API_KEY "
            "environment variable."
        ),
    )
    parser.add_argument(
        "--service-url",
        help=(
            "URL of the transcription service. Overrides the "
            "SYNCTOON_SERVICE_URL environment variable."
        ),
    )
    return parser.parse_args()


def resolve_path(cli_value: Optional[str], env_var: str, default: Path) -> Path:
    """Resolve a path from CLI input, environment variables, or defaults."""

    if cli_value:
        path = Path(cli_value).expanduser()
    else:
        env_value = os.getenv(env_var)
        path = Path(env_value).expanduser() if env_value else default

    if not path.exists():
        raise FileNotFoundError(
            f"Unable to locate required file: '{path}'. "
            f"Provide a valid path via CLI flag or the {env_var} environment variable."
        )

    if not path.is_file():
        raise ValueError(
            f"Expected a file for '{path}', but a different type of path was provided."
        )

    return path


def resolve_api_key(cli_value: Optional[str]) -> str:
    """Resolve the Google API key from CLI or environment variables."""

    api_key = cli_value or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(
            "Missing Google API key. Provide it using --api-key or set the "
            "GOOGLE_API_KEY environment variable."
        )
    return api_key


def resolve_service_url(cli_value: Optional[str]) -> str:
    """Resolve the transcription service URL from CLI or environment variables."""

    return (
        cli_value
        or os.getenv("SYNCTOON_SERVICE_URL")
        or DEFAULT_SERVICE_URL
    )


def main() -> int:
    args = parse_arguments()

    try:
        transcript_path = resolve_path(
            args.transcript, "SYNCTOON_TRANSCRIPT_PATH", DEFAULT_TRANSCRIPT_PATH
        )
        audio_path = resolve_path(
            args.audio, "SYNCTOON_AUDIO_PATH", DEFAULT_AUDIO_PATH
        )
        api_key = resolve_api_key(args.api_key)
        service_url = resolve_service_url(args.service_url)
    except (FileNotFoundError, ValueError) as error:
        print(f"Configuration error: {error}", file=sys.stderr)
        return 1

    files = [
        ("transcript", str(transcript_path), "text/plain"),
        ("audio", str(audio_path), "application/octet-stream"),
    ]

    service = TranscriptionService(files=files, url=service_url)
    response_json = service.send_request()

    if not isinstance(response_json, dict):
        print(
            "Transcription service returned an unexpected response. "
            "Ensure the service is running and reachable.",
            file=sys.stderr,
        )
        return 1

    transcript = response_json.get("transcript")
    if not transcript:
        print(
            "No transcript found in the transcription service response. "
            "Skipping analysis steps.",
            file=sys.stderr,
        )
        return 1

    analyzer = TextAnalyzer(api_key=api_key)

    head_movement = analyzer.get_head_movement_instructions(transcript)
    time.sleep(6)
    eyes_movement = analyzer.get_eyes_movement_instructions(transcript)
    time.sleep(6)
    character = analyzer.get_character(transcript, characters)
    time.sleep(6)
    emotion_result = analyzer.get_emotion(transcript, emotions)
    time.sleep(6)
    body_action = analyzer.get_body_action(transcript, body_actions)
    time.sleep(6)
    intensity = analyzer.get_intensity(transcript)
    time.sleep(6)
    zoom = analyzer.get_zoom(transcript)
    time.sleep(6)
    screen_mode_result = analyzer.get_screen_mode(transcript, screen_mode)

    update_values(response_json, head_movement, "head_direction", "M")
    update_values(response_json, eyes_movement, "eyes_direction", "M")
    update_values(response_json, character, "character", 1)
    update_values(response_json, emotion_result, "emotion", 1)
    update_values(response_json, body_action, "body_action", 3)
    update_values(response_json, intensity, "intensity", 1)
    update_values(response_json, zoom, "zoom", 0)
    update_values(response_json, screen_mode_result, "screen_mode", 1)

    add_phonemes(response_json)
    update_assets(response_json)
    video_frames_info(response_json)

    with open("output_test.json", "w") as json_file:
        json.dump(response_json, json_file, indent=4)

    return 0


if __name__ == "__main__":
    sys.exit(main())
