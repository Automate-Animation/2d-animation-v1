

# Function to get the direction for a given number
def get_direction_for_number(data, type):

    # Create a dictionary to map numbers to their corresponding head_direction
    direction_map = {}

    # Populate the dictionary
    for entry in data:
        start = entry['text']['start']
        end = entry['text']['end']
        direction = entry["direction"]
        
        # Map each number in the range from start to end (exclusive) to the direction
        for num in range(start, end):
            direction_map[num] = direction

    return direction_map

import json

# Step 1: Read the JSON file
with open('/home/oye/Documents/animation_software/2d-animation-v1/core/requests/gentle.json', 'r') as file:
    data = json.load(file)  # Load the JSON data from the file

eyes_dict = get_direction_for_number(eyes, "direction")
head_dict = get_direction_for_number(head, "direction")
print(head_dict.get(0))
# print(data['words'])
for i, each_data in enumerate(data['words']):
    each_data["head_direction"] = head_dict.get(i,"M")
    each_data["eyes_direction"] = eyes_dict.get(i,"M")


# Step 3: Save the modified JSON data back to the file
with open('gentle_updated.json', 'w') as file:
    json.dump(data, file, indent=4)  # Save the JSON data with indentation for readability

