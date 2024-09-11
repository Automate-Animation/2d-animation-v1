import json
from utils.constants import emotions, body_actions, screen_mode, characters

with open("utils/mouth_image.json", "r") as json_file:
    response_json = json.load(json_file)

# print(response_json)
happy_mouth = ["happy", "content", "sarcasm", "crazy", "evil_laugh", "lust", "silly"]
print(emotions)


def update_assets(data):
    for each_data in data["words"]:
        # emotion
        if int(each_data["intensity"]) == 2:
            each_data["emotion_name"] = emotions.get(each_data["emotion"]) + "_2"
        else:
            each_data["emotion_name"] = emotions.get(each_data["emotion"])

        # character
        each_data["character_name"] = "character_" + str(each_data["character"])

        # background
        each_data["background_name"] = screen_mode.get(int(each_data["screen_mode"]))[
            "name"
        ]

        # body
        each_data["body_name"] = body_actions.get(int(each_data["body_action"]))

        # mouth
        if each_data["emotion_name"] in happy_mouth:
            emotion = "happy"
        else:
            emotion = "sad"
        phonemes_frame_details = []
        for phoneme in each_data["phonemes_frame"]:
            detail = {}
            detail["phoneme"] = phoneme["name"]
            detail["frame"] = phoneme["frames"]
            detail["emotion"] = emotion
            detail["mouth_name"] = response_json[phoneme["name"]][emotion]
            phonemes_frame_details.append(detail)
        each_data["phonemes_frame_details"] = phonemes_frame_details
    return data
