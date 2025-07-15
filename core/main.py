import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

from brain_requests.speach_aligner import TranscriptionService
from brain_requests.text_aligner import TextAnalyzer
from brain_requests.utils import update_values
import json
import time
from utils.add_phonemes import add_phonemes
from utils.constants import emotions, body_actions, screen_mode, characters
from utils.update_character_asset_name import update_assets
from utils.frame_info_generator import video_frames_info

def get_transcription(audio_path, transcript_path):
    """
    Sends a request to the TranscriptionService to get the transcription of an audio file.
    """
    try:
        logging.info("Getting transcription...")
        url = "http://localhost:49153/transcriptions?async=false"
        files = [
            ("transcript", (transcript_path, open(transcript_path, "r"), "text/plain")),
            ("audio", (audio_path, open(audio_path, "rb"), "application/octet-stream")),
        ]
        service = TranscriptionService(files=files)
        response = service.send_request()
        logging.info("Transcription received successfully.")
        return response
    except Exception as e:
        logging.error(f"Error getting transcription: {e}")
        return None


def analyze_text(api_key, transcript):
    """
    Analyzes the transcript to get various instructions for the animation.
    """
    try:
        logging.info("Analyzing text...")
        analyzer = TextAnalyzer(api_key=api_key)
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
        logging.info("Text analysis completed successfully.")
        return {
            "head_movement": head_movement,
            "eyes_movement": eyes_movement,
            "character": character,
            "emotions": emotions,
            "body_action": body_action,
            "intensity": intensity,
            "zoom": zoom,
            "screen_mode": screen_mode,
        }
    except Exception as e:
        logging.error(f"Error analyzing text: {e}")
        return None


def update_transcription(response_json, analysis_results):
    """
    Updates the transcription with the analysis results.
    """
    try:
        logging.info("Updating transcription...")
        update_values(response_json, analysis_results["head_movement"], "head_direction", "M")
        update_values(response_json, analysis_results["eyes_movement"], "eyes_direction", "M")
        update_values(response_json, analysis_results["character"], "character", 1)
        update_values(response_json, analysis_results["emotions"], "emotion", 1)
        update_values(response_json, analysis_results["body_action"], "body_action", 3)
        update_values(response_json, analysis_results["intensity"], "intensity", 1)
        update_values(response_json, analysis_results["zoom"], "zoom", 0)
        update_values(response_json, analysis_results["screen_mode"], "screen_mode", 1)
        logging.info("Transcription updated successfully.")
    except Exception as e:
        logging.error(f"Error updating transcription: {e}")


def process_video_data(response_json):
    """
    Processes the video data by adding phonemes, updating assets, and generating frame info.
    """
    try:
        logging.info("Processing video data...")
        add_phonemes(response_json)
        update_assets(response_json)
        video_frames_info(response_json)
        logging.info("Video data processed successfully.")
    except Exception as e:
        logging.error(f"Error processing video data: {e}")


def run_core_logic(audio_path, transcript_path, google_api_key):
    """
    Runs the core logic of the script.
    """
    response_json = get_transcription(audio_path, transcript_path)
    if response_json:
        transcript = response_json["transcript"]
        analysis_results = analyze_text(google_api_key, transcript)
        if analysis_results:
            update_transcription(response_json, analysis_results)
            process_video_data(response_json)

            with open("output_test.json", "w") as json_file:
                json.dump(response_json, json_file, indent=4)

import csv
from PIL import Image
from image_manager.CharacterManager import CharacterManager
import os
from PIL import Image, ImageOps
import statistics
import numpy as np

def get_character_image(manager, row):
    """
    Retrieves the character image and metadata based on the row data.
    """
    character = row["Character"]
    emotion = row["Emotion"]
    body = row["Body"]
    head_direction = row["Head_Direction"]
    eyes_direction = row["Eyes_Direction"]
    background = row["Background"]
    mouth_emotion = row["Mouth_Emotion"]
    mouth_name = row["Mouth_Name"]
    zoom = int(row["Zoom"])
    blink = bool(row["Blink"])

    key = (
        character
        + emotion
        + body
        + head_direction
        + eyes_direction
        + background
        + mouth_emotion
        + mouth_name
        + str(zoom)
        + str(blink)
    )

    return manager.get_character(
        Character=character,
        Emotion=emotion,
        Body=body,
        Head_Direction=head_direction,
        Eyes_Direction=eyes_direction,
        Background=background,
        Mouth_Emotion=mouth_emotion,
        Mouth_Name=mouth_name,
        zoom=zoom,
        blink=blink,
    ), key


def save_frame(image, key, counter):
    """
    Saves the image frame to a file.
    """
    image_file = f"video_frames/{key}.png"
    image.save(image_file)
    print(f"Frame {counter} saved as {image_file}")


def run_frame_generator_logic(csv_file_path):
    """
    Runs the frame generator logic.
    """
    try:
        logging.info("Running frame generator logic...")
        base_path = "./images/characters"
        metadata_file = "./images/metadata/metadata.json"
        manager = CharacterManager(base_path, metadata_file)
        frame_data = {"key_counter": {}, "frame_key": {}}
        video_frames_path = "./video_frames"

        # Create video_frames directory if it doesn't exist
        if not os.path.exists(video_frames_path):
            os.makedirs(video_frames_path)

        files = [f for f in os.listdir(video_frames_path)]
        for each_file in files:
            key_name = each_file.split(".")[0]
            if key_name:
                frame_data["key_counter"][each_file.split(".")[0]] = 1

        with open(csv_file_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for counter, row in enumerate(reader):
                image, key = get_character_image(manager, row)

                if key not in frame_data["key_counter"]:
                    frame_data["key_counter"][key] = 1
                    save_frame(image, key, counter)
                else:
                    frame_data["key_counter"][key] += 1

                frame_data["frame_key"][counter] = key
                logging.info(f"{counter}  --  {key}")

        with open("frameCreationInfo.json", "w") as outfile:
            json.dump(frame_data, outfile)
        logging.info("Frame generator logic completed successfully.")
    except Exception as e:
        logging.error(f"Error in frame generator logic: {e}")

import argparse
from datetime import datetime
from os.path import isfile, join
import cv2

def convert_frames_to_video(path_in, path_out, fps):
    """
    Converts frames to a video.
    """
    frame_array = []
    files = [f for f in os.listdir(path_in) if isfile(join(path_in, f)) and f.endswith(".png")]
    files.sort()

    first_frame = join(path_in, files[0])
    img = cv2.imread(first_frame)

    if img is None:
        print(f"Error: Unable to read the image {first_frame}")
        return

    height, width, layers = img.shape
    size = (width, height)
    out = cv2.VideoWriter(path_out, cv2.VideoWriter_fourcc(*"DIVX"), fps, size)

    with open("./frameCreationInfo.json") as f:
        frame_data = json.load(f)

    for counter in range(len(frame_data["frame_key"])):
        filename = join(path_in, frame_data["frame_key"][str(counter)] + ".png")
        img = cv2.imread(filename)

        if img is None:
            print(f"Error: Unable to read the image {filename}")
            continue

        print(f"{counter} : {filename}")
        out.write(img)

    out.release()
    print(f"Video saved to {path_out}")


def run_frame_to_video_logic(video_name):
    """
    Runs the frame to video logic.
    """
    try:
        logging.info("Running frame to video logic...")
        path_in = "./video_frames/"
        path_out = f"./videos/{video_name}.avi"
        fps = 24.0

        # Create videos directory if it doesn't exist
        if not os.path.exists("./videos"):
            os.makedirs("./videos")

        convert_frames_to_video(path_in, path_out, fps)
        logging.info("Frame to video logic completed successfully.")
    except Exception as e:
        logging.error(f"Error in frame to video logic: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="2D Animation V1")
    parser.add_argument("--audio_path", type=str, required=True, help="Path to the audio file.")
    parser.add_argument("--transcript_path", type=str, required=True, help="Path to the transcript file.")
    parser.add_argument("--google_api_key", type=str, required=True, help="Google API key.")
    parser.add_argument("--video_name", type=str, default="output", help="Name of the output video file.")
    args = parser.parse_args()

    run_core_logic(args.audio_path, args.transcript_path, args.google_api_key)
    run_frame_generator_logic("video_frames_info.csv")
    run_frame_to_video_logic(args.video_name)
