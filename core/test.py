import math

data = {
    "alignedWord": "colorful",
    "case": "success",
    "end": 0.8200000000000001,
    "endOffset": 13,
    "phones": [
        {"duration": 0.12, "phone": "k_B"},
        {"duration": 0.1, "phone": "ah_I"},
        {"duration": 0.08, "phone": "l_I"},
        {"duration": 0.07, "phone": "er_I"},
        {"duration": 0.05, "phone": "f_I"},
        {"duration": 0.03, "phone": "ah_I"},
        {"duration": 0.07, "phone": "l_E"},
    ],
    "start": 0.3,
    "startOffset": 5,
    "word": "colorful",
    "head_direction": "M",
    "eyes_direction": "M",
    "character": 1,
    "emotion": 1,
    "body_action": 41,
    "intensity": 1,
    "zoom": 0,
    "screen_mode": 3,
    "phonemes": ["K", "AH1", "L", "ER0", "F", "AH0", "L"],
    "init_frame": 8,
    "final_frame": 20,
    "diff": 12,
    "emotion_name": "happy",
    "character_name": "character_1",
    "background_name": "white",
    "body_name": "thinking",
}


# Update the JSON data with the new phonemes_frame list
data["phonemes_frame"] = distribute_frames(data)

# Output the updated data with phonemes_frame
print(data["phonemes_frame"])
