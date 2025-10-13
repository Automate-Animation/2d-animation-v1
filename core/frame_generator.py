import csv
from PIL import Image
from image_manager.CharacterManager import CharacterManager
import os
import json
from PIL import Image, ImageOps
import statistics
import numpy as np


def parse_blink_value(value):
    """Parse blink values from CSV input into a strict boolean."""
    if isinstance(value, bool):
        return value

    if value is None:
        return False

    if isinstance(value, (int, float)):
        return value == 1

    normalized = str(value).strip().lower()
    return normalized in {"true", "1"}

# Assuming manager is defined and contains the get_character method
# Replace manager.get_character with your own method to load character images
base_path = "./images/characters"
metadata_file = "./images/metadata/metadata.json"
manager = CharacterManager(base_path, metadata_file)
frame_data = {"key_counter": {}, "frame_key": {}}
mypath = "./video_frames"
files = [f for f in os.listdir(mypath)]
for each_file in files:
    key_name = each_file.split(".")[0]
    if key_name:
        frame_data["key_counter"][each_file.split(".")[0]] = 1


def save_frames_from_csv(csv_file):
    # Open the CSV file
    with open(csv_file, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        counter = 0
        # Loop through each row in the CSV file
        for row in reader:
            print(counter)

            # Retrieve metadata from each row
            # frame = row["Frame"]
            character = row["Character"]
            emotion = row["Emotion"]
            body = row["Body"]
            head_direction = row["Head_Direction"]
            eyes_direction = row["Eyes_Direction"]
            background = row["Background"]
            mouth_emotion = row["Mouth_Emotion"]
            mouth_name = row["Mouth_Name"]
            zoom = int(row["Zoom"])
            blink = parse_blink_value(row.get("Blink"))
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
            # Check if image already exists in video_frames folder
            image_file = f"video_frames/{key}.png"

            if key not in frame_data["key_counter"]:
                frame_data["key_counter"][key] = 1

                # Check if image file already exists
                if os.path.exists(image_file):
                    print(
                        f"Frame {counter} - Image {image_file} already exists, using existing image"
                    )
                else:
                    # Retrieve image and metadata using manager.get_character
                    image, metadata = manager.get_character(
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
                    )

                    # Save the image for the current frame
                    image.save(image_file)
                    print(f"Frame {counter} saved as {image_file}")
            else:
                frame_data["key_counter"][key] = frame_data["key_counter"][key] + 1
            frame_data["frame_key"][counter] = key
            print(counter, " -- ", key)

            counter += 1

            # Optionally display the image
            # image.show()
    with open("frameCreationInfo.json", "w") as outfile:
        json.dump(frame_data, outfile)


def main():
    """Main function to run frame generation."""
    save_frames_from_csv("video_frames_info.csv")


if __name__ == "__main__":
    main()
