import json
import math

import nltk

nltk.download("averaged_perceptron_tagger_eng")

from g2p_en import G2p

g2p = G2p()
# file_name = 'G:/Projects/speech aligner/kamal speech aliner/speach_aliner/app/json/json_data_for_frame/kamal.json'
# with open(file_name, 'r') as f:
#   data = json.load(f)


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

        number_of_phonemes = len(each_data["phonemes"])
        if number_of_phonemes < each_data["diff"]:
            phonemes_frame = {}
            num, div = each_data["diff"], number_of_phonemes
            count_frame = [num // div + (1 if x < num % div else 0) for x in range(div)]

            for i in range(len(count_frame)):
                phonemes_frame[each_data["phonemes"][i]] = count_frame[i]

        else:
            phonemes_frame = {}
            limited_frame = each_data["diff"]
            for each_phoneme in each_data["phonemes"]:
                if limited_frame > 0:
                    phonemes_frame[each_phoneme] = 1
                    limited_frame -= 1
                else:
                    phonemes_frame[each_phoneme] = 0
        each_data["phonemes_frame"] = phonemes_frame

    data["FRAME_PER_SECOUND"] = FRAME_PER_SECOUND
    data["AUDO_END_TIME"] = AUDO_END_TIME
    data["TOTAL_VIDEO_FRAMES"] = AUDO_END_TIME * FRAME_PER_SECOUND + 1
    data["MODE"] = "normal"

    return data
