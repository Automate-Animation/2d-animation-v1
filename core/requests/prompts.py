prompts = {
    "head_movement_instructions": """Review the following text carefully. Based on the text, provide instructions for head movements that would look natural as if you were engaging with the story. The only directions available are Left (L), Right (R), and Center (M). The head movements should align with the narrative flow and emphasize key elements of the story without being overly dynamic.

        text:
        ```
        {text}
        ```
        Total Length: {total_length}
        Word Count: {word_count}

        Make sure to cover all significant segments of the text and do not omit any part. Ensure the list includes all relevant entries based on the above criteria.


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
        
        Make sure to cover all significant segments of the text and do not omit any part. Ensure the list includes all relevant entries based on the above criteria.

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

        Make sure to cover all significant segments of the text and do not omit any part. Ensure the list includes all relevant entries based on the above criteria.

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
    "emotion_selector": """

            Review the following text carefully. Based on the text, provide instructions to reflect the character's emotional state as described. The emotions should align with the narrative flow and emphasize key emotional elements of the story.
            Given the following list of Emotions and their types:
            ```
            {emotions}

            ```
            text:
            ```
            {text}
            ```

            Total Length: {total_length}
            Word Count: {word_count}

            Make sure to cover all significant segments of the text and do not omit any part. Ensure the list includes all relevant entries based on the above criteria.


            Return the instrunction in JSON format
            ```
            [
                {{
                    "text": {{"start": X, "end": Y}}, // start and end should be based on the word count of the text.
                    "emotion": N // choose only one: 1, 2..
                }},
                ...
                {{
                    "text": {{"start": X, "end": `word_count`}}, // start and end should be based on the word count of the text.
                    "emotion": N // choose only one: 1, 2..
                }},
            ]
            ```
            """,
    "body_action_selector": """
            Review the following text carefully. Based on the text, provide instructions for body actions that would look dramatic and full of action. The available actions should emphasize key elements of the story, capturing dynamic moments without being too subtle.
            Given the following list of body actions and their types:

            ```
            {body_actions}

            ```
            ```
            {text}
            ```

            Total Length: {total_length}
            Word Count: {word_count}

            Make sure to cover all significant segments of the text and do not omit any part. Ensure the list includes all relevant entries based on the above criteria.


            Return the instrunction in JSON format
            ```
            [
                {{
                    "text": {{"start": X, "end": Y}}, // start and end should be based on the word count of the text.
                    "body_action": N // choose only one: 1, 2..
                }},
                ...
                {{
                    "text": {{"start": X, "end": `word_count`}}, // start and end should be based on the word count of the text.
                    "body_action": N // choose only one: 1, 2..
                }},
            ]
            ```
            """,
    "intensity_selector": """
        Review the following text carefully. Identify and mark the moments of high intensity and emotional significance, ensuring that most of the text is marked with normal intensity. Only assign high intensity to parts that are particularly dramatic, intense, or show significant emotion.

        Do not return an empty list. Ensure that there is at least one entry in the list, even if the intensity is normal.

        text:
        ```
        {text}
        ```

        Total Length: {total_length}
        Word Count: {word_count}

        Guidelines:
            Normal Intensity (2): Apply this to most of the text where the action or emotion is standard or subdued.
            High Intensity (1): Apply this to moments of extreme action or significant emotion that are crucial to the story's dramatic impact.

        Make sure to cover all significant segments of the text and do not omit any part. Ensure the list includes all relevant entries based on the above criteria.

        Return the instrunction in JSON format
        ```
        [
            {{
                "text": {{"start": X, "end": Y}}, // start and end should be based on the word count of the text.
                "intensity": N // choose only one: 1, 2
            }},
            ...
            {{
                "text": {{"start": X, "end": `word_count`}}, // start and end should be based on the word count of the text.
                "intensity": N // choose only one: 1, 2
            }},
        ]
        ```


        """,
}
