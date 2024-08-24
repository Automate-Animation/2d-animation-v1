import google.generativeai as genai


class TextAnalyzer:
    def __init__(self, api_key, model_name="gemini-pro"):
        self.api_key = api_key
        self.model_name = model_name
        self._configure_api()
        self.model = genai.GenerativeModel(self.model_name)
        self.chat = self.model.start_chat(history=[])

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

    def create_prompt(self, text):
        """
        Create a prompt based on the input text for generating instructions.

        Args:
            text (str): The input text for which to create the prompt.

        Returns:
            str: The formatted prompt for the model.
        """
        total_length, word_count = self.analyze_string(text)
        prompt = f"""
        Review the following text carefully. Based on the text, provide instructions for head movements that would look natural as if you were engaging with the story. The only directions available are Left (L), Right (R), and Center (M). The head movements should align with the narrative flow and emphasize key elements of the story without being overly dynamic.

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
        ```
        """
        return prompt

    def get_head_movement_instructions(self, text):
        """
        Get head movement instructions based on the input text.

        Args:
            text (str): The input text to analyze.

        Returns:
            str: The response from the generative model.
        """
        prompt = self.create_prompt(text)
        response = self.chat.send_message(prompt)
        return response.text


# Usage example
if __name__ == "__main__":
    # Replace YOUR_API_KEY_HERE with your actual API key
    GOOGLE_API_KEY = "AIzaSyCpzGmA1jU2601Nyg1hMDposu_8WHYBdQY"

    # Initialize the TextAnalyzer class
    analyzer = TextAnalyzer(api_key=GOOGLE_API_KEY)

    # Test with a sample string
    text = """In a colorful meadow, a tiny seed named Sprout dreamed of becoming tall and strong. One day, a wind whispered stories of adventure and courage to Sprout. Inspired, Sprout decided to push through the soil. Despite facing hungry insects and pesky weeds, it persevered. Days turned into weeks, and Sprout grew into a majestic sunflower. From above, it saw the world and knew it had achieved its dreams. 
    Sprout became a symbol of bravery and determination, inspiring all who saw it."""

    # Get head movement instructions
    instructions = analyzer.get_head_movement_instructions(text)
    print(instructions)
