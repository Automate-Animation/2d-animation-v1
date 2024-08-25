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
text = """
Hey, remember that hike we did last weekend? It was amazing!
Totally! The views were breathtaking, and the fresh air was so invigorating.
I know, right? I felt like I was on top of the world. And that little waterfall we stumbled upon was such a pleasant surprise.
Me too! I love how nature can just pop up like that. It's like a hidden treasure.
Speaking of treasures, I found this really cool rock on the way back down. It has this unique pattern on it.
Wow, that's awesome! Can I see it?
Sure. Here.
It's beautiful! You should keep it as a souvenir.
Maybe I will. I'll definitely frame it and hang it up.
That's a great idea. It'll be a constant reminder of that unforgettable adventure."""
total_length, word_count = analyze_string(text)
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

print(f"Total Length: {total_length}")
print(f"Word Count: {word_count}")

prompt = f"""

Review the following text carefully. Based on the text, provide instructions to reflect the character's emotional state as described. The emotions should align with the narrative flow and emphasize key emotional elements of the story.
Given the following list of Emotions and their types:

```
{emotions}

```
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
        "emotion": N // choose only one: 1, 2..
    }},
    ...
    {{
        "text": {{"start": X, "end": `word_count`}}, // start and end should be based on the word count of the text.
        "emotion": N // choose only one: 1, 2..
    }},
]
```


"""
# Example: Starting a chat session and sending a message
chat = model.start_chat(history=[])

print("---")
print(prompt)
print("---")
response = chat.send_message(prompt)

# Print the response
print(response.text)
