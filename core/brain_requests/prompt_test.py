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
print(f"Total Length: {total_length}")
print(f"Word Count: {word_count}")

prompt = f"""

Review the following text carefully. Identify and mark the moments that would benefit from different zoom levels to make the video more engaging. Assign appropriate zoom levels based on the content's significance, emotional impact, or to highlight key points and details.

Do not return an empty list. Ensure that there is at least one entry in the list, even if all the zoom levels are normal.

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
Return the instrunction in JSON format
```
[
    {{
        "text": {{"start": X, "end": Y}}, // start and end should be based on the word count of the text.
        "zoom": N // choose only one: 0 (Normal Zoom), 1 (Moderate Zoom), 2 (High Zoom)
    }},
    ...
    {{
        "text": {{"start": X, "end": `word_count`}}, // start and end should be based on the word count of the text.
        "zoom": N // choose only one: 0 (Normal Zoom), 1 (Moderate Zoom), 2 (High Zoom)   
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
