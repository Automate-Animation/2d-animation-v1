import json
import math

import nltk

nltk.download("averaged_perceptron_tagger_eng")

from g2p_en import G2p

g2p = G2p()
# file_name = 'G:/Projects/speech aligner/kamal speech aliner/speach_aliner/app/json/json_data_for_frame/kamal.json'
# with open(file_name, 'r') as f:
#   data = json.load(f)


def distribute_frames(data):
    # Extract phonemes
    phonemes = data["phonemes"]

    init_frame = data["init_frame"]
    final_frame = data["final_frame"]
    total_frames = final_frame - init_frame

    # Since we don't have the phones data, we'll distribute frames equally across phonemes
    phoneme_count = len(phonemes)
    frames_per_phoneme = total_frames // phoneme_count  # Get base frames per phoneme
    leftover_frames = total_frames % phoneme_count  # Get remaining frames to distribute

    phonemes_frame = []

    # Distribute frames for each phoneme
    for idx, phoneme in enumerate(phonemes):
        frames = frames_per_phoneme
        if leftover_frames > 0:  # Distribute leftover frames one by one
            frames += 1
            leftover_frames -= 1

        # Append the phoneme with its frame count to the list
        phonemes_frame.append({"name": phoneme, "frames": frames})

    return phonemes_frame


def add_phonemes(data, FRAME_PER_SECOUND=24, EXTRA_TIME=0):
    FRAME_PER_SECOUND = FRAME_PER_SECOUND
    AUDO_END_TIME = data["words"][-1]["end"]
    EXTRA_TIME = EXTRA_TIME
    AUDO_END_TIME = math.ceil(float(AUDO_END_TIME) + EXTRA_TIME)

    print("FRAME_PER_SECOUND:", FRAME_PER_SECOUND)
    print("AUDO_END_TIME  : ", AUDO_END_TIME)
    # print(data['fragments'][0])
    for each_data in data.get("words"):
        each_data["phonemes"] = g2p(each_data["word"])
        print(each_data["phonemes"])
        each_data["init_frame"] = math.ceil(
            float(each_data["start"]) * FRAME_PER_SECOUND
        )
        each_data["final_frame"] = math.ceil(
            float(each_data["end"]) * FRAME_PER_SECOUND
        )

        # each_data['diff'] = math.floor(  (each_data['final_frame'] - each_data['init_frame']) / len(each_data['phonemes']))
        each_data["diff"] = math.ceil(
            (each_data["final_frame"] - each_data["init_frame"])
        )
        each_data["phonemes_frame"] = distribute_frames(each_data)

    data["FRAME_PER_SECOUND"] = FRAME_PER_SECOUND
    data["AUDO_END_TIME"] = AUDO_END_TIME
    data["TOTAL_VIDEO_FRAMES"] = AUDO_END_TIME * FRAME_PER_SECOUND + 1
    data["MODE"] = "normal"

    return data
