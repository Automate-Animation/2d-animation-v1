import csv
import json
from datetime import datetime


def video_frames_info(data):

    # Get current date and time
    current_time = datetime.now().strftime("-%Y-%m-%d:%H-%M-%S")

    # Define the CSV file path with date and time
    csv_file_path = f"video_frames_info.csv"
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
        "Zoom",
        "Blink",
    ]
    frame_counter = 0
    # Create CSV file and write data
    with open(csv_file_path, mode="w", newline="") as file:
        writer = csv.writer(file)

        # Write header
        writer.writerow(head)

        # Write data for each frame
        total_frames = data["TOTAL_VIDEO_FRAMES"]
        word_info = data["words"]

        character = word_info[0]["character_name"]
        emotion = word_info[0]["emotion_name"]
        body = word_info[0]["body_name"]
        head_direction = word_info[0]["head_direction"]
        eyes_direction = (
            word_info[0]["emotion_name"] + "_" + word_info[0]["eyes_direction"]
        )
        background = word_info[0]["background_name"]
        zoom = word_info[0]["zoom"]

        alignedWord = ""
        start = ""
        end = ""
        mouth_emotion = "happy"
        mouth_name = "m_b_close_h"

        blink_sequence = ["02", "03", "04"]  # Blinking pattern for eyes_direction
        blink_frame_interval = 80  # Add blink after every 80 frames
        blink_counter = 0

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
                    eyes_direction = (
                        each_fagment["emotion_name"]
                        + "_"
                        + each_fagment["eyes_direction"]
                    )
                    background = each_fagment["background_name"]
                    zoom = each_fagment["zoom"]

                    phoneme_frame_details = each_fagment["phonemes_frame_details"]

                    for phoneme_data in phoneme_frame_details:
                        phoneme = phoneme_data["phoneme"]
                        mouth_emotion = phoneme_data["emotion"]
                        mouth_name = phoneme_data["mouth_name"]
                        frame = phoneme_data["frame"]

                        for _ in range(frame):
                            # Check if blink should occur in this frame
                            if blink_counter == blink_frame_interval:
                                blink_counter = 0  # Reset blink counter
                                for blink_value in blink_sequence:
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
                                            f"{blink_value}",  # Add blink values to eyes_direction
                                            background,
                                            phoneme,
                                            mouth_emotion,
                                            mouth_name,
                                            zoom,
                                            "True",  # Blink is True
                                        ]
                                    )
                                    frame_counter += 1
                                    blink_counter += 1
                            else:
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
                                        zoom,
                                        "False",  # Blink is False
                                    ]
                                )
                                frame_counter += 1
                                blink_counter += 1

            alignedWord = ""
            phoneme = ""
            if mouth_emotion == "happy":
                mouth_name = "m_b_close_h"
            else:
                mouth_name = "m_b_close_s"

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
                    zoom,
                    "False",  # Blink is False
                ]
            )

            frame_counter += 1

    print(f"CSV file created: {csv_file_path}")
