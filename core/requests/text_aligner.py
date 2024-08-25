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

    def emotion_selector(self, text, emotions):
        """
        Analyzes the given text and generates a JSON response that reflects the character's emotional state based on the provided emotions.

        Args:
            text (str): The text to analyze for emotional content.
            emotions (dict): A dictionary mapping emotion IDs to their descriptions.

        Returns:
            dict: A JSON object where each entry contains:
                - "text": A dictionary with "start" and "end" indicating the segment of the text.
                - "emotion": The selected emotion based on the provided emotions dictionary.

        Example:
            text = "John was thrilled to see his old friend again."
            emotions = {
                "1": "happy",
                "2": "sad",
                "3": "angry",
                "4": "bore",
                "5": "content",
                "6": "glare",
                "7": "sarcasm",
                "8": "worried",
                "9": "crazy",
                "10": "evil_laugh",
                "11": "lust",
                "12": "shock",
                "13": "silly",
                "14": "spoked",
            }
            result = emotion_selector(text, emotions)
            # result would be a JSON object reflecting the emotional content of the text.
        """
        total_length, word_count = self.analyze_string(text)
        template = self.prompts["emotion_selector"]
        prompt = template.format(
            text=text,
            total_length=total_length,
            word_count=word_count,
            emotions=emotions,
        )
        response = self.chat.send_message(prompt)
        return self.extract_json_content(response.text)

    def body_action_selector(self, text, body_actions):
        """
        Analyzes the given text and generates a JSON response that reflects dramatic body actions based on the provided body actions list.

        Args:
            text (str): The text to analyze for body actions.
            body_actions (dict): A dictionary mapping body action IDs to their descriptions.

        Returns:
            dict: A JSON object where each entry contains:
                - "text": A dictionary with "start" and "end" indicating the segment of the text.
                - "body_action": The selected body action based on the provided body actions dictionary.

        Example:
            text = "He leaped across the room with an intense look on his face."
            body_actions = {
                "1": "achieve",
                "2": "answer",
                "3": "explain",
                "4": "me",
                "5": "not_me",
                "6": "question",
                "7": "technical",
                "8": "why",
                "9": "achieve",
                "10": "answer",
                "11": "chilling",
                "12": "come",
                "13": "confuse",
                "14": "crazy",
                "15": "dancing",
                "16": "explain",
                "17": "feeling_down",
                "18": "hi",
                "19": "i",
                "20": "idea",
                "21": "idk",
                "22": "joy",
                "23": "jumping",
                "24": "kung_fu",
                "25": "love",
                "27": "meditation",
                "28": "model",
                "30": "paper",
                "31": "praying",
                "32": "question",
                "33": "running",
                "34": "search",
                "35": "shy",
                "36": "singing",
                "37": "sneaky",
                "38": "standing",
                "39": "technical",
                "40": "that",
                "41": "thinking",
                "42": "this",
                "43": "what",
                "44": "why",
                "45": "winner",
                "46": "yeah",
                "47": "you",
            }
            result = body_action_selector(text, body_actions)
            # result would be a JSON object reflecting the dramatic body actions described in the text.
        """
        total_length, word_count = self.analyze_string(text)
        template = self.prompts["body_action_selector"]
        prompt = template.format(
            text=text,
            total_length=total_length,
            word_count=word_count,
            body_actions=body_actions,
        )
        response = self.chat.send_message(prompt)
        return self.extract_json_content(response.text)

    def intensity_selector(self, text):
        total_length, word_count = self.analyze_string(text)
        template = self.prompts["intensity_selector"]
        prompt = template.format(
            text=text,
            total_length=total_length,
            word_count=word_count,
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
    emotions = {
        "1": "happy",
        "2": "sad",
        "3": "angry",
        "4": "bore",
        "5": "content",
        "6": "glare",
        "7": "sarcasm",
        "8": "worried",
        "9": "crazy",
        "10": "evil_laugh",
        "11": "lust",
        "12": "shock",
        "13": "silly",
        "14": "spoked",
    }
    body_actions = {
        "1": "achieve",
        "2": "answer",
        "3": "explain",
        "4": "me",
        "5": "not_me",
        "6": "question",
        "7": "technical",
        "8": "why",
        "9": "achieve",
        "10": "answer",
        "11": "chilling",
        "12": "come",
        "13": "confuse",
        "14": "crazy",
        "15": "dancing",
        "16": "explain",
        "17": "feeling_down",
        "18": "hi",
        "19": "i",
        "20": "idea",
        "21": "idk",
        "22": "joy",
        "23": "jumping",
        "24": "kung_fu",
        "25": "love",
        "27": "meditation",
        "28": "model",
        "30": "paper",
        "31": "praying",
        "32": "question",
        "33": "running",
        "34": "search",
        "35": "shy",
        "36": "singing",
        "37": "sneaky",
        "38": "standing",
        "39": "technical",
        "40": "that",
        "41": "thinking",
        "42": "this",
        "43": "what",
        "44": "why",
        "45": "winner",
        "46": "yeah",
        "47": "you",
    }
    # Test with a sample string
    text = """In a colorful meadow, a tiny seed named Sprout dreamed of becoming tall and strong. One day, a wind whispered stories of adventure and courage to Sprout. Inspired, Sprout decided to push through the soil. Despite facing hungry insects and pesky weeds, it persevered. Days turned into weeks, and Sprout grew into a majestic sunflower. From above, it saw the world and knew it had achieved its dreams. 
    Sprout became a symbol of bravery and determination, inspiring all who saw it."""

    # Get head movement instructions
    # instructions = analyzer.character_selector(text, characters)
    # instructions = analyzer.emotion_selector(text, emotions)
    # instructions = analyzer.body_action_selector(text, body_actions)
    instructions = analyzer.intensity_selector(text)
    print(instructions)
