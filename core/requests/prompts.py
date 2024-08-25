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
                "direction": ""  // choose only one: L, R, or M
            }},
            ...
            {{
                "text": {{"start": --, "end": {word_count}}},  // start and end should be based on the word count of the text.
                "direction": ""  // choose only one: L, R, or M
            }},
        ]
        ```""",
    "eye_movement_instructions": """Review the following text carefully. Based on the text, provide instructions for eye movements that would look natural as if you were engaging with the story. The only directions available are Left (L), Right (R), and Center (M). The eye movements should align with the narrative flow and emphasize key elements of the story without being overly dynamic.

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
                "direction": ""  // choose only one: L, R, or M
            }},
            ...
            {{
                "text": {{"start": --, "end": {word_count}}},  // start and end should be based on the word count of the text.
                "direction": ""  // choose only one: L, R, or M
            }},
        ]
        ```""",
    "character_selector": """
        Review the following text carefully. Based on the text, provide instructions for each character that would look natural as if you were engaging with the story.
        Given the following list of characters and their types:

        ```
        {characters}

        ```
        Given the list of characters above, the characters should align with the narrative flow and emphasize key elements of the story without being overly dynamic.

        Task:

        Analyze the text below and identify:

            If the text is a dialogue between characters:
                Determine how many characters are speaking.
                Provide their IDs and the ranges of their dialogue based on the word count.

            If the text is a monologue (one person speaking):
                Use only one character.
                Indicate their ID and the range of the text they are speaking.
        text:
        ```
        {text}
        ```

        Total Length: {total_length}
        Word Count: {word_count}

        Return the instrunction in JSON format
        ```
        [
            {{
                "text": {{"start": X, "end": Y}}, // start and end should be based on the word count of the text.
                "character": N // choose only one: 1, 2..
            }},
            ...
            {{
                "text": {{"start": X, "end": `word_count`}}, // start and end should be based on the word count of the text.
                "character": N // choose only one: 1, 2..
            }},
        ]
        ```
        """,
}
