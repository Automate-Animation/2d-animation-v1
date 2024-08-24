prompts = {
    "head_movement_instructions": """Review the following text carefully. Based on the text, provide instructions for head movements that would look natural as if you were engaging with the story. The only directions available are Left (L), Right (R), and Center (M). The head movements should align with the narrative flow and emphasize key elements of the story without being overly dynamic.

        text:
        ```
        {text}
        ```
        Total Length: {total_length}
        Word Count: {word_count}

        Return the instructions in JSON format:
        ```
        [
            {{
                "text": {{"start": 0, "end": 4}},  // start and end should be based on the word count of the text.
                "head_direction": ""  // choose only one: L, R, or M
            }},
            ...
            {{
                "text": {{"start": --, "end": {word_count}}},  // start and end should be based on the word count of the text.
                "head_direction": ""  // choose only one: L, R, or M
            }},
        ]
        ```"""
}
