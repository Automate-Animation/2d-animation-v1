import json
import google.generativeai as genai
from prompts import prompts


class TextAnalyzer:
    def __init__(self, api_key, model_name="gemini-pro", prompt_file=prompts):
        self.api_key = api_key
        self.model_name = model_name
        self.prompt_file = prompt_file
        self._configure_api()
        self.model = genai.GenerativeModel(self.model_name)
        self.chat = self.model.start_chat(history=[])
        self.prompts = prompts

    def _configure_api(self):
        genai.configure(api_key=self.api_key)

    def analyze_string(self, text):
        """
        Calculate the total length and word count of the string.

        Args:
            text (str): The input text to analyze.

        Returns:
            tuple: A tuple containing total length and word count.
        """
        total_length = len(text)
        word_count = len(text.split())
        return total_length, word_count

    def remove_json_code_block_markers(self, response):
        # Remove the ```JSON and ``` markers from the response
        return response.replace("```JSON\n", "").replace("```", "")

    def extract_json_content(self, response):
        # Initialize variables to store the start and end indices of the JSON content
        start_index = None
        end_index = None

        # Search for the first occurrence of '[' or '{' in the string
        for i, char in enumerate(response):
            if char == "[" or char == "{":
                start_index = i
                break

        # Search for the last occurrence of ']' or '}' in the string
        for i, char in enumerate(reversed(response)):
            if char == "]" or char == "}":
                end_index = len(response) - i
                break

        # If both start and end indices are found, extract the content
        if (
            start_index is not None
            and end_index is not None
            and start_index < end_index
        ):
            return json.loads(response[start_index:end_index])
        else:
            return ""  # Return an empty string if no valid JSON content is found

    def get_head_movement_instructions(self, text):
        """
        Get head movement instructions based on the input text.

        Args:
            text (str): The input text to analyze.

        Returns:
            str: The response from the generative model.
        """
        total_length, word_count = self.analyze_string(text)
        template = self.prompts["head_movement_instructions"]
        prompt = template.format(
            text=text, total_length=total_length, word_count=word_count
        )
        response = self.chat.send_message(prompt)
        return self.extract_json_content(response.text)

    def get_eyes_movement_instructions(self, text):
        """
        Get eyes movement instructions based on the input text.

        Args:
            text (str): The input text to analyze.

        Returns:
            str: The response from the generative model.
        """
        total_length, word_count = self.analyze_string(text)
        template = self.prompts["eye_movement_instructions"]
        prompt = template.format(
            text=text, total_length=total_length, word_count=word_count
        )
        response = self.chat.send_message(prompt)
        return self.extract_json_content(response.text)

    def character_selector(self, text, characters):
        """
        Analyzes the given text to identify and select characters based on their dialogue or monologue.

        This method prepares a prompt using the provided text and character information, sends it to a chat service for processing, and extracts the JSON-formatted response that includes character dialogue or monologue details.

        Parameters:
        - text (str): The text to be analyzed, which may contain dialogue or monologue.
        - characters (dict): A dictionary mapping character IDs to their names and types, used to identify who is speaking in the text.

        Returns:
        - list: A list of dictionaries, each containing:
            - "text" (dict): A dictionary with "start" and "end" keys indicating the word count range of the text spoken by a character.
            - "character" (int): The ID of the character speaking the specified text.

        Example:
        >>> characters = {'1': {'name': 'Hero', 'type': 'Protagonist'}, '2': {'name': 'Villain', 'type': 'Antagonist'}}
        >>> text = "Hero: I will save the day. Villain: Not if I can help it!"
        >>> selector.character_selector(text, characters)
        [{'text': {'start': 0, 'end': 4}, 'character': 1},
        {'text': {'start': 5, 'end': 11}, 'character': 2}]
        """
        total_length, word_count = self.analyze_string(text)
        template = self.prompts["character_selector"]
        prompt = template.format(
            text=text,
            total_length=total_length,
            word_count=word_count,
            characters=characters,
        )
        response = self.chat.send_message(prompt)
        return self.extract_json_content(response.text)


# Usage example
if __name__ == "__main__":
    # Replace YOUR_API_KEY_HERE with your actual API key
    GOOGLE_API_KEY = "AIzaSyCpzGmA1jU2601Nyg1hMDposu_8WHYBdQY"

    # Initialize the TextAnalyzer class
    analyzer = TextAnalyzer(api_key=GOOGLE_API_KEY)

    characters = {
        "1": {"name": "Hero", "type": "Protagonist"},
        "2": {"name": "Villain", "type": "Antagonist"},
        "3": {"name": "Sidekick", "type": "Supporting"},
        "4": {"name": "Mentor", "type": "Supporting"},
    }
    # Test with a sample string
    text = """In a colorful meadow, a tiny seed named Sprout dreamed of becoming tall and strong. One day, a wind whispered stories of adventure and courage to Sprout. Inspired, Sprout decided to push through the soil. Despite facing hungry insects and pesky weeds, it persevered. Days turned into weeks, and Sprout grew into a majestic sunflower. From above, it saw the world and knew it had achieved its dreams. 
    Sprout became a symbol of bravery and determination, inspiring all who saw it."""

    # Get head movement instructions
    instructions = analyzer.character_selector(text, characters)
    print(instructions)
