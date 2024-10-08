from brain_requests.speach_aligner import TranscriptionService
from brain_requests.text_aligner import TextAnalyzer
from brain_requests.utils import update_values
import json
import time
from utils.add_phonemes import add_phonemes
from utils.constants import emotions, body_actions, screen_mode, characters
from utils.update_character_asset_name import update_assets
from utils.frame_info_generator import video_frames_info

if __name__ == "__main__":
    url = "http://localhost:49153/transcriptions?async=false"
    files = [
        (
            "transcript",
            "/home/oye/Documents/dailyYGStories/A Family Secret Almost Ruined My Wedding—Am I Wrong for Excluding My Brother?.txt",
            "text/plain",
        ),
        (
            "audio",
            "/home/oye/Documents/dailyYGStories/A Family Secret Almost Ruined My Wedding—Am I Wrong for Excluding My Brother?.mp3",
            "application/octet-stream",
        ),
    ]

    GOOGLE_API_KEY = "AIzaSyCpzGmA1jU2601Nyg1hMDposu_8WHYBdQY"

    # Initialize the TextAnalyzer class
    analyzer = TextAnalyzer(api_key=GOOGLE_API_KEY)

    service = TranscriptionService(files=files)
    response_json = service.send_request()
    transcript = response_json["transcript"]
    head_movement = analyzer.get_head_movement_instructions(transcript)
    time.sleep(6)
    eyes_movement = analyzer.get_eyes_movement_instructions(transcript)
    time.sleep(6)
    character = analyzer.get_character(transcript, characters)
    time.sleep(6)
    emotions = analyzer.get_emotion(transcript, emotions)
    time.sleep(6)
    body_action = analyzer.get_body_action(transcript, body_actions)
    time.sleep(6)
    intensity = analyzer.get_intensity(transcript)
    time.sleep(6)
    zoom = analyzer.get_zoom(transcript)
    time.sleep(6)
    screen_mode = analyzer.get_screen_mode(transcript, screen_mode)

    update_values(response_json, head_movement, "head_direction", "M")
    update_values(response_json, eyes_movement, "eyes_direction", "M")
    update_values(response_json, character, "character", 1)
    update_values(response_json, emotions, "emotion", 1)
    update_values(response_json, body_action, "body_action", 3)
    update_values(response_json, intensity, "intensity", 1)
    update_values(response_json, zoom, "zoom", 0)
    update_values(response_json, screen_mode, "screen_mode", 1)

    # add Phonemes and Frames
    add_phonemes(response_json)
    update_assets(response_json)
    video_frames_info(response_json)
    with open("output_test.json", "w") as json_file:
        json.dump(response_json, json_file, indent=4)

    # with open("output_test.json", "r") as json_file:
    #     response_json = json.load(json_file)
    # video_frames_info(response_json)
    # print(response_json)
    # with open("update_assets_output_fi.json", "w") as json_file:
    #     json.dump(response_json, json_file, indent=4)
