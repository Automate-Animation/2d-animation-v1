import argparse
import json
import os
from datetime import datetime

import cv2

# Initialize parser
parser = argparse.ArgumentParser()

# Adding optional argument
parser.add_argument("-n", "--name", help="name of video")

def convert_frames_to_video(pathIn, pathOut, fps, frame_data, cv2_module=cv2):
    """
    Optimized OpenCV method with better codec and settings
    """
    try:
        # Load the first image to get video dimensions
        frame_keys = frame_data.get("frame_key")
        if not frame_keys:
            print("Error: Metadata is missing frame_key entries.")
            return False

        first_frame_key = frame_keys.get("0") if isinstance(frame_keys, dict) else None
        if first_frame_key is None:
            print("Error: Metadata does not contain a first frame entry.")
            return False

        first_frame_path = pathIn + first_frame_key + ".png"

        if not os.path.exists(first_frame_path):
            print(
                "Error: First frame not found at"
                f" {first_frame_path}. Please ensure frames are generated."
            )
            return False

        img = cv2_module.imread(first_frame_path)

        if img is None:
            print(f"Error: Unable to read the image {first_frame_path}")
            return False

        height, width, layers = img.shape
        size = (width, height)

        # Use H.264 codec for better compression and quality
        fourcc = cv2_module.VideoWriter_fourcc(*"mp4v")  # or 'H264' if available
        out = cv2_module.VideoWriter(pathOut, fourcc, fps, size)

        if not out.isOpened():
            print("Error: VideoWriter could not be opened")
            return False

        # Process frames in order using frame_data
        total_frames = len(frame_keys)
        print(f"Creating video with {total_frames} frames...")

        for counter in range(total_frames):
            try:
                frame_key = (
                    frame_keys[str(counter)]
                    if isinstance(frame_keys, dict)
                    else frame_keys[counter]
                )
            except (KeyError, IndexError):
                print(
                    f"Warning: Metadata missing frame entry for index {counter}, skipping frame."
                )
                continue

            filename = pathIn + frame_key + ".png"
            img = cv2_module.imread(filename)

            if img is None:
                print(f"Error: Unable to read the image {filename}")
                continue

            if counter % 100 == 0:  # Progress indicator every 100 frames
                print(
                    f"Processing frame {counter}/{total_frames} ({(counter/total_frames)*100:.1f}%)"
                )

            out.write(img)

        out.release()
        print(f"Video successfully saved to {pathOut}")
        return True

    except Exception as e:
        print(f"OpenCV method failed: {e}")
        return False


def main():
    # Define the input folder containing the frames
    pathIn = "./video_frames/"

    # Read arguments from command line
    args = parser.parse_args()

    if args.name:
        pathOut = f"./videos/{args.name}.mp4"
        name = args.name
    else:
        today = datetime.now()
        pathOut = f"./videos/{str(today)}.mp4"
        name = today

    print(f"Creating video with file name: {name}")

    metadata_path = "./frameCreationInfo.json"

    if not os.path.exists(metadata_path):
        print(
            "Error: Metadata file frameCreationInfo.json not found. "
            "Please run the frame generator before creating a video."
        )
        return

    with open(metadata_path) as metadata_file:
        frame_data = json.load(metadata_file)

    # Set frames per second (FPS) for the video
    fps = 24.0

    # Convert the frames to a video
    convert_frames_to_video(pathIn, pathOut, fps, frame_data)


if __name__ == "__main__":
    main()
