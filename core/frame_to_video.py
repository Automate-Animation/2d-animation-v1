import argparse
import json
import os
from datetime import datetime
from os.path import isfile, join

import cv2
import numpy as np

# Initialize parser
parser = argparse.ArgumentParser()

# Adding optional argument
parser.add_argument("-n", "--name", help="name of video")

# Load the frame data from JSON
frame_data = open("./frameCreationInfo.json")
frame_data = json.load(frame_data)


def convert_frames_to_video(pathIn, pathOut, fps):
    frame_array = []

    # Get a list of PNG files from the directory
    files = [
        f for f in os.listdir(pathIn) if isfile(join(pathIn, f)) and f.endswith(".png")
    ]

    # Sort files based on the number in the filename (if applicable)
    files.sort()

    # Load the first image to get video dimensions
    first_frame = pathIn + files[0]
    img = cv2.imread(first_frame)

    if img is None:
        print(f"Error: Unable to read the image {first_frame}")
        return

    height, width, layers = img.shape
    size = (width, height)

    # Create VideoWriter object
    out = cv2.VideoWriter(pathOut, cv2.VideoWriter_fourcc(*"DIVX"), fps, size)

    # Iterate over the frame keys from the frame_data JSON
    for counter in range(len(frame_data["frame_key"])):
        filename = pathIn + frame_data["frame_key"][str(counter)] + ".png"
        img = cv2.imread(filename)

        if img is None:
            print(f"Error: Unable to read the image {filename}")
            continue

        print(counter, " : ", filename)

        # Write the image frame to the video
        out.write(img)

    out.release()
    print(f"Video saved to {pathOut}")


def main():
    # Define the input folder containing the frames
    pathIn = "./video_frames/"

    # Read arguments from command line
    args = parser.parse_args()

    if args.name:
        pathOut = f"./videos/{args.name}.avi"
        name = args.name
    else:
        today = datetime.now()
        pathOut = f"./videos/{str(today)}.avi"
        name = today

    print(f"Creating video with file name: {name}")

    # Set frames per second (FPS) for the video
    fps = 24.0

    # Convert the frames to a video
    convert_frames_to_video(pathIn, pathOut, fps)


if __name__ == "__main__":
    main()
