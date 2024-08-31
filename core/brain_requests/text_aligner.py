import json
import google.generativeai as genai
from .prompts import prompts
from .validater import (
    CharacterSchema,
    validate_data,
    HeadDirectionSchema,
    EyesDirectionSchema,
    EmotionSchema,
    IntensitySchema,
    ZoomSchema,
    BodyActionSchema,
    ScreenModeSchema,
)
from .utils import retry


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
        print("Configuring API with provided API key...")
        genai.configure(api_key=self.api_key)

    def analyze_string(self, text):
        total_length = len(text)
        word_count = len(text.split())
        # print(
        #     f"Text analysis complete: Total length = {total_length}, Word count = {word_count}"
        # )
        return total_length, word_count

    def _send_message_and_extract(self, prompt, schema):
        # Sends a prompt to the chat model and extracts the JSON content
        max_attempts = 3
        attempts = 0

        while attempts < max_attempts:
            response = self.chat.send_message(prompt)
            data = self.extract_json_content(response.text)
            status, message = validate_data(data, schema)

            if status:
                break

            # Update prompt with validation message
            prompt = prompt + "\n" + str(message)
            attempts += 1

        return data

    def remove_json_code_block_markers(self, response):
        return response.replace("```JSON\n", "").replace("```", "")

    def extract_json_content(self, response):
        start_index = None
        end_index = None

        for i, char in enumerate(response):
            if char == "[" or char == "{":
                start_index = i
                break

        for i, char in enumerate(reversed(response)):
            if char == "]" or char == "}":
                end_index = len(response) - i
                break

        if (
            start_index is not None
            and end_index is not None
            and start_index < end_index
        ):
            print("JSON content successfully extracted.")
            data = json.loads(response[start_index:end_index])
            print("-------------")
            print(data)
            print("-------------")
            return data
        else:
            print("No valid JSON content found.")
            return ""

    def get_head_movement_instructions(self, text):
        print("Getting head movement instructions...")
        total_length, word_count = self.analyze_string(text)
        template = self.prompts["head_movement_instructions"]
        prompt = template.format(
            text=text, total_length=total_length, word_count=word_count
        )
        schema = HeadDirectionSchema(many=True)
        return self._send_message_and_extract(prompt, schema)

    def get_eyes_movement_instructions(self, text):
        print("Getting eyes movement instructions...")
        total_length, word_count = self.analyze_string(text)
        template = self.prompts["eye_movement_instructions"]
        prompt = template.format(
            text=text, total_length=total_length, word_count=word_count
        )
        schema = EyesDirectionSchema(many=True)
        return self._send_message_and_extract(prompt, schema)

    @retry(max_attempts=3, delay=1)
    def get_character(self, text, characters):
        print("Analyzing character from text...")
        total_length, word_count = self.analyze_string(text)
        template = self.prompts["character_selector"]
        prompt = template.format(
            text=text,
            total_length=total_length,
            word_count=word_count,
            characters=characters,
        )
        schema = CharacterSchema(many=True)
        response = self._send_message_and_extract(prompt, schema)
        return response

    def get_emotion(self, text, emotions):
        print("Analyzing emotion from text...")
        total_length, word_count = self.analyze_string(text)
        template = self.prompts["emotion_selector"]
        prompt = template.format(
            text=text,
            total_length=total_length,
            word_count=word_count,
            emotions=emotions,
        )
        schema = EmotionSchema(many=True)
        return self._send_message_and_extract(prompt, schema)

    def get_body_action(self, text, body_actions):
        print("Analyzing body action from text...")
        total_length, word_count = self.analyze_string(text)
        template = self.prompts["body_action_selector"]
        prompt = template.format(
            text=text,
            total_length=total_length,
            word_count=word_count,
            body_actions=body_actions,
        )
        schema = BodyActionSchema(many=True)
        return self._send_message_and_extract(prompt, schema)

    def get_intensity(self, text):
        print("Analyzing intensity from text...")
        total_length, word_count = self.analyze_string(text)
        template = self.prompts["intensity_selector"]
        prompt = template.format(
            text=text,
            total_length=total_length,
            word_count=word_count,
        )
        schema = IntensitySchema(many=True)
        return self._send_message_and_extract(prompt, schema)

    def get_zoom(self, text):
        print("Analyzing zoom from text...")
        total_length, word_count = self.analyze_string(text)
        template = self.prompts["get_zoom"]
        prompt = template.format(
            text=text,
            total_length=total_length,
            word_count=word_count,
        )
        schema = ZoomSchema(many=True)
        return self._send_message_and_extract(prompt, schema)

    def get_screen_mode(self, text, screen_mode):
        print("Analyzing zoom from text...")
        total_length, word_count = self.analyze_string(text)
        template = self.prompts["get_screen_mode"]
        prompt = template.format(
            text=text,
            total_length=total_length,
            screen_mode=screen_mode,
            word_count=word_count,
        )
        schema = ScreenModeSchema(many=True)
        return self._send_message_and_extract(prompt, schema)


# Usage example
if __name__ == "__main__":
    print("Starting main execution...")
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

    print("Running text analysis methods...")
    instructions = analyzer.get_character(text, characters)
    instructions = analyzer.get_emotion(text, emotions)
    instructions = analyzer.get_body_action(text, body_actions)
    instructions = analyzer.get_intensity(text)
    instructions = analyzer.get_zoom(text)
    print(instructions)

    print("Main execution finished.")
