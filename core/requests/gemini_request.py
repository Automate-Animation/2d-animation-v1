import google.generativeai as genai

# Replace YOUR_API_KEY_HERE with your actual API key
GOOGLE_API_KEY = "AIzaSyCpzGmA1jU2601Nyg1hMDposu_8WHYBdQY"

# Configure the API key
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize the model
model = genai.GenerativeModel("gemini-pro")


def analyze_string(text):
    # Calculate the total length of the string
    total_length = len(text)

    # Count the words in the string by splitting it into a list of words
    word_count = len(text.split())

    # Return both the total length and word count
    return total_length, word_count


# Test the function with a sample string
text = """In a colorful meadow, a tiny seed named Sprout dreamed of becoming tall and strong. One day, a wind whispered stories of adventure and courage to Sprout. Inspired, Sprout decided to push through the soil. Despite facing hungry insects and pesky weeds, it persevered. Days turned into weeks, and Sprout grew into a majestic sunflower. From above, it saw the world and knew it had achieved its dreams. 
Sprout became a symbol of bravery and determination, inspiring all who saw it."""
total_length, word_count = analyze_string(text)

print(f"Total Length: {total_length}")
print(f"Word Count: {word_count}")

prompt = f"""

Review the following text carefully. Based on the text, provide instructions for head movements that would look natural as if you were engaging with the story. The only directions available are Left (L), Right (R), and Center (M). The head movements should align with the narrative flow and emphasize key elements of the story without being overly dynamic.text:
```
{text}
```
Total Length: {total_length}
Word Count: {word_count}

return the instrunction in json format
```
[
    {{
        "text": {{"start": 0, "end": 4}}, // start and end should be based on the word count of the text.
        "head_direction": "" // choose only one: L, R, or M
    }},
    ...
    {{
        "text": {{"start": --, "end": `word_count`}}, // start and end should be based on the word count of the text.
        "head_direction": "" // choose only one: L, R, or M
    }},
]
```


"""
# Example: Starting a chat session and sending a message
chat = model.start_chat(history=[])
response = chat.send_message(prompt)

# Print the response
print(response.text)
