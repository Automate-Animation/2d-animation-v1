import csv
import json
from datetime import datetime

# Sample JSON data (replace this with your actual JSON input)
data = {
    "transcript": "In a colorful meadow, a tiny seed named Sprout dreamed of becoming tall and strong...",
    "words": [
        {
            "alignedWord": "it",
            "case": "success",
            "end": 33.62,
            "endOffset": 477,
            "phones": [
                {"duration": 0.07, "phone": "ih_B"},
                {"duration": 0.14, "phone": "t_E"},
            ],
            "start": 33.41,
            "startOffset": 475,
            "word": "it",
            "head_direction": "M",
            "eyes_direction": "M",
            "character": 1,
            "emotion": 5,
            "body_action": 20,
            "intensity": 1,
            "zoom": 0,
            "screen_mode": 3,
            "phonemes": ["IH1", "T"],
            "init_frame": 802,
            "final_frame": 807,
            "diff": 5,
            "phonemes_frame": {"IH1": 3, "T": 2},
            "emotion_name": "content",
            "character_name": "character_1",
            "background_name": "white",
            "body_name": "idea",
            "phonemes_frame_details": {
                "IH1": {
                    "phoneme": "IH1",
                    "frame": 3,
                    "emotion": "happy",
                    "mouth_name": "a_e_h",
                },
                "T": {
                    "phoneme": "T",
                    "frame": 2,
                    "emotion": "happy",
                    "mouth_name": "th_h",
                },
            },
        }
    ],
    "FRAME_PER_SECOUND": 24,
    "AUDO_END_TIME": 34,
    "TOTAL_VIDEO_FRAMES": 817,
    "MODE": "normal",
}


def video_frames_info(data):

    # Get current date and time
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Define the CSV file path with date and time
    csv_file_path = f"video_frames_info_{current_time}.csv"
    head = [
        "Frame",
        "Word",
        "Start_Time",
        "End_Time",
        "Character",
        "Emotion",
        "Body",
        "Head_Direction",
        "Eyes_Direction",
        "Background",
        "Phoneme",
        "Mouth_Emotion",
        "Mouth_Name",
    ]
    frame_counter = 0
    # Create CSV file and write data
    with open(csv_file_path, mode="w", newline="") as file:
        writer = csv.writer(file)

        # Write header
        writer.writerow(head)

        alignedWord = ""
        start = ""
        end = ""
        character = ""
        emotion = ""
        body = ""
        head_direction = ""
        eyes_direction = ""
        background = ""
        mouth_emotion = "happy"
        mouth_name = "m_b_close_h"
        # Write data for each frame
        total_frames = data["TOTAL_VIDEO_FRAMES"]
        word_info = data["words"]
        # phoneme_frame_details = word_info['phonemes_frame_details'][0]

        while frame_counter <= total_frames:
            for each_fagment in word_info:
                if frame_counter >= int(
                    each_fagment["init_frame"]
                ) and frame_counter <= int(each_fagment["final_frame"]):

                    alignedWord = each_fagment["alignedWord"]
                    start = each_fagment["start"]
                    end = each_fagment["end"]
                    character = each_fagment["character_name"]
                    emotion = each_fagment["emotion_name"]
                    body = each_fagment["body_name"]
                    head_direction = each_fagment["head_direction"]
                    eyes_direction = each_fagment["eyes_direction"]
                    background = each_fagment["background_name"]

                    phoneme_frame_details = each_fagment["phonemes_frame_details"]

                    for phoneme_data in phoneme_frame_details:
                        phoneme = phoneme_data["phoneme"]
                        mouth_emotion = phoneme_data["emotion"]
                        mouth_name = phoneme_data["mouth_name"]
                        frame = phoneme_data["frame"]
                        for _ in range(frame):
                            writer.writerow(
                                [
                                    frame_counter,
                                    alignedWord,
                                    start,
                                    end,
                                    character,
                                    emotion,
                                    body,
                                    head_direction,
                                    eyes_direction,
                                    background,
                                    phoneme,
                                    mouth_emotion,
                                    mouth_name,
                                ]
                            )
                            frame_counter += 1
            alignedWord = ""
            phoneme = ""
            mouth_emotion = "happy"
            mouth_name = "m_b_close_h"
            writer.writerow(
                [
                    frame_counter,
                    alignedWord,
                    start,
                    end,
                    character,
                    emotion,
                    body,
                    head_direction,
                    eyes_direction,
                    background,
                    phoneme,
                    mouth_emotion,
                    mouth_name,
                ]
            )

            frame_counter += 1

    print(f"CSV file created: {csv_file_path}")
