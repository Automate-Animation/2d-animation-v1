prompts = {
    "head_movement_instructions": """
    
        Carefully review the text below and create head movement instructions that feel natural, as if you're actively engaging with the story. You can choose from three directions for the head: Left (L), Right (R), and Mid (M). The head should stay mostly in the Mid position to maintain focus, but slight shifts to Left or Right can highlight key moments in the narrative.

        Make sure the movements flow smoothly with the story, aligning with its structure without being overly animated.

        text:
        ```
        {text}
        ```
        Total Length: {total_length}
        Word Count: {word_count}

        Cover all important sections of the text and ensure no parts are left out.

        Return the instructions in JSON format:
        ```
        [
            {{
                "text": {{"start": 0, "end": 4}},  // start and end should be based on the word count of the text.
                "head_direction": ""  // choose only one: L, R, or M
            }},
           ..
            {{
                "text": {{"start": --, "end": {word_count}}},  // start and end should be based on the word count of the text.
                "head_direction": ""  // choose only one: L, R, or M
            }},
        ]
        ```""",
    "eye_movement_instructions": """
        
        Review the following text carefully. When the character is talking to the audience, ensuring that 90% of the time, the character looks at the camera (M), and the remaining 10% is split between looking Left (L) and Right (R) randomly. For example, the eye movement might be 3 seconds Mid (M), 1 second Right (R), and 5 seconds Mid (M), 3 seconds Left (L), and so on. The available directions for eye movements are Left (L), Right (R), and Mid (M). The movements should align with the narrative flow and natural human responses to the story.
        text:

        ```
        {text}
        ```
        Total Length: {total_length}
        Word Count: {word_count}

        Guidelines for Eye Movement:

            Mid (M): Use this direction 90% of the time, especially when the character is directly engaging with the audience or focusing on the main content of the narrative.
            Left (L): Use this direction when the narrative suggests looking towards something or someone to the left, indicating curiosity, reaction, or attention to a leftward focus.
            Right (R): Use this direction when the narrative suggests looking towards something or someone to the right, indicating curiosity, reaction, or attention to a rightward focus.
       
        Make sure to cover all significant segments of the text and do not omit any part. Ensure the list includes all relevant entries based on the above criteria.
        Do not return an empty list.

        Return the instructions in JSON format:
        ```
        [
            {{
                "text": {{"start": 0, "end": 4}},  // start and end should be based on the word count of the text.
                "eyes_direction": ""  // choose only one: L, R, or M
            }},
           ..
            {{
                "text": {{"start": --, "end": {word_count}}},  // start and end should be based on the word count of the text.
                "eyes_direction": ""  // choose only one: L, R, or M
            }},
        ]
        ```""",
    "character_selector": """
        Review the following text carefully. Based on the text, provide instructions for each character that would look natural as if you were engaging with the story. 
        Given the following list of characters and their types:

        ```
        {characters}

        ```
        Given the list of characters above, Pick the characters should align with the narrative flow and emphasize key elements of the story without being overly dynamic.

        Task:

        Analyze the text below and identify:

            If the text is a dialogue between characters:
                Determine how many characters are speaking.
                Provide their IDs and the ranges of their dialogue based on the word count.

            If the text is a monologue (one person speaking):
                Use only one character.
                Indicate their ID and the range of the text they are speaking.

        Guidelines:

            Ensure all significant segments of the text are covered, and do not omit any part.
            Always select a character; do not return an empty list.
            If unsure which character to choose, default to the "Hero" (ID: 1).

        Make sure to cover all significant segments of the text and do not omit any part. Ensure the list includes all relevant entries based on the above criteria.
        Do not return an empty list. ,

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

            Do not return an empty list.

            Return the instrunction in JSON format
            ```
            [
                {{
                    "text": {{"start": X, "end": Y}}, // start and end should be based on the word count of the text.
                    "emotion": N // choose only one: 1, 2..
                }},
               ..
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

            Guidelines:
                Assign body actions to all significant segments of the text, ensuring that every part is covered.
                Emphasize dynamic and dramatic moments that align with the narrative flow.
                Do not leave any segment without a body action. Ensure the list includes all relevant entries based on the criteria.
                Do not return an empty list. Each segment must have a designated body action, even if the action is less dramatic.


            Return the instrunction in JSON format
            ```
            [
                {{
                    "text": {{"start": X, "end": Y}}, // start and end should be based on the word count of the text.
                    "body_action": N // choose only one: 1, 2..
                }},
               ..
                {{
                    "text": {{"start": X, "end": `word_count`}}, // start and end should be based on the word count of the text.
                    "body_action": N // choose only one: 1, 2..
                }},
            ]
            ```
            """,
    "intensity_selector": """
        Review the following text carefully. Identify and mark the moments of high intensity and emotional significance, ensuring that most of the text is marked with normal intensity. Only assign high intensity to parts that are particularly dramatic, intense, or show significant emotion.

        Do not return an empty list. ,

        text:
        ```
        {text}
        ```

        Total Length: {total_length}
        Word Count: {word_count}

        Guidelines:
            Normal Intensity (1): Apply this to most of the text where the action or emotion is standard or subdued.
            High Intensity (2): Apply this to moments of extreme action or significant emotion that are crucial to the story's dramatic impact.

        Make sure to cover all significant segments of the text and do not omit any part. Ensure the list includes all relevant entries based on the above criteria.
        Do not return an empty list.

        Return the instrunction in JSON format
        ```
        [
            {{
                "text": {{"start": X, "end": Y}}, // start and end should be based on the word count of the text.
                "intensity": N // choose only one: 1, 2
            }},
           ..
            {{
                "text": {{"start": X, "end": `word_count`}}, // start and end should be based on the word count of the text.
                "intensity": N // choose only one: 1, 2
            }},
        ]
        ```


        """,
    "get_zoom": """

        Review the following text carefully. Identify and mark the moments that would benefit from different zoom levels to make the video more engaging. Assign appropriate zoom levels based on the content's significance, emotional impact, or to highlight key points and details.

        text:
        ```
        {text}
        ```

        Total Length: {total_length}
        Word Count: {word_count}

        Guidelines for Zoom Levels:

            Normal Zoom (0): Use this for most of the text where the action or dialogue is routine or does not require emphasis.
            Moderate Zoom (1): Apply this to moments that need some focus to enhance viewer engagement, such as when highlighting an important point, detail, or subtle emotion.
            High Zoom (2): Use this for moments of significant emotion, dramatic impact, or crucial content that requires intense focus.

        Ensure that all significant segments of the text are covered and none are omitted. The list should include all relevant entries based on the criteria above.
        Do not return an empty list. ,

        Return the instrunction in JSON format
        ```
        [
            {{
                "text": {{"start": X, "end": Y}}, // start and end should be based on the word count of the text.
                "zoom": N // choose only one: 0 (Normal Zoom), 1 (Moderate Zoom), 2 (High Zoom)
            }},
           ..
            {{
                "text": {{"start": X, "end": `word_count`}}, // start and end should be based on the word count of the text.
                "zoom": N // choose only one: 0 (Normal Zoom), 1 (Moderate Zoom), 2 (High Zoom)   
            }},
        ]
        ```


        """,
    "get_screen_mode": """
    
        Carefully review the following text. Identify and select the most thematically appropriate background for each section to enhance the viewer's engagement and clarity of the story. The background should reflect the setting and context of the story, ensuring smooth transitions and maintaining thematic consistency throughout.

        Given the following list of screen modes and their types:

        ```
        {screen_mode}

        ```

        text:
        ```
        {text}
        ```

        Guidelines:

            Select screen modes that correspond to the specific context or setting described in the story (e.g., a café setting for a scene in a café).
            Avoid changing backgrounds too frequently; focus on significant shifts in the story's location or environment.
            Ensure the background aligns with the key thematic elements and keeps the viewer immersed in the story.
        Do not return an empty list. ,

        Return the instrunction in JSON format
        ```
        [
            {{
                "text": {{"start": X, "end": Y}}, // start and end should be based on the word count of the text.
                "screen_mode": N // choose only one: 1, 2, 3, 4, 5,
           ..
            {{
                "text": {{"start": X, "end": `word_count`}}, // start and end should be based on the word count of the text.
                "screen_mode": N // choose only one: 1, 2, 3, 4, 5,
            }},
        ]
        ```
        """,
}
