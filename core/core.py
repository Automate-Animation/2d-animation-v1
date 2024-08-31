from brain_requests.speach_aligner import TranscriptionService
from brain_requests.text_aligner import TextAnalyzer
from brain_requests.utils import update_values
import json
import time
from brain_requests.add_phonemes import add_phonemes


if __name__ == "__main__":
    url = "http://localhost:49153/transcriptions?async=false"
    files = [
        (
            "transcript",
            "/home/oye/Documents/animation_software/2d-animation-v1/example/story/story-2.txt",
            "text/plain",
        ),
        (
            "audio",
            "/home/oye/Documents/animation_software/2d-animation-v1/example/story/story-2-01.m4a",
            "application/octet-stream",
        ),
    ]
    characters = {
        "1": {"name": "Hero", "type": "Protagonist"},
        "2": {"name": "Villain", "type": "Antagonist"},
        "3": {"name": "Sidekick", "type": "Supporting"},
        "4": {"name": "Mentor", "type": "Supporting"},
    }
    emotions = {
        "1": "happy",
        "2": "sad",
        "3": "angry",
        "4": "bore",
        "5": "content",
        "6": "glare",
        "7": "sarcasm",
        "8": "worried",
        "9": "crazy",
        "10": "evil_laugh",
        "11": "lust",
        "12": "shock",
        "13": "silly",
        "14": "spoked",
    }
    body_actions = {
        "1": "achieve",
        "2": "answer",
        "3": "explain",
        "4": "me",
        "5": "not_me",
        "6": "question",
        "7": "technical",
        "8": "why",
        "9": "achieve",
        "10": "answer",
        "11": "chilling",
        "12": "come",
        "13": "confuse",
        "14": "crazy",
        "15": "dancing",
        "16": "explain",
        "17": "feeling_down",
        "18": "hi",
        "19": "i",
        "20": "idea",
        "21": "idk",
        "22": "joy",
        "23": "jumping",
        "24": "kung_fu",
        "25": "love",
        "27": "meditation",
        "28": "model",
        "30": "paper",
        "31": "praying",
        "32": "question",
        "33": "running",
        "34": "search",
        "35": "shy",
        "36": "singing",
        "37": "sneaky",
        "38": "standing",
        "39": "technical",
        "40": "that",
        "41": "thinking",
        "42": "this",
        "43": "what",
        "44": "why",
        "45": "winner",
        "46": "yeah",
        "47": "you",
    }

    screen_mode = {
        "1": {
            "name": "office",
            "details": "Use this background when the content is formal, professional, or business-related.",
        },
        "2": {
            "name": "explanation",
            "details": "Apply this background when providing detailed explanations, tutorials, or educational content.",
        },
        "3": {
            "name": "white",
            "details": "Use this background for a clean, minimalistic look, ideal for content that requires focus without distractions.",
        },
        "4": {
            "name": "plain",
            "details": "Apply this background for neutral content that doesn’t need any specific emphasis or theme.",
        },
        "5": {
            "name": "green",
            "details": "Use this background when you plan to add a virtual background or need flexibility for future editing.",
        },
    }

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
    with open("output_fi.json", "w") as json_file:
        json.dump(response_json, json_file, indent=4)

    # with open("output_fi.json", "r") as json_file:
    #     response_json = json.load(json_file)
    # print(response_json)

    # with open("add_phonemes_output_fi.json", "w") as json_file:
    #     json.dump(response_json, json_file, indent=4)
