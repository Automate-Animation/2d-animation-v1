from image_manager.CharacterManager import CharacterManager
import os
import json
from PIL import Image, ImageOps
import statistics
import numpy as np

# Example usage
base_path = (
    "/home/oye/Documents/animation_software/2d-animation-v1/core/images/characters"
)
metadata_file = "/home/oye/Documents/animation_software/2d-animation-v1/core/images/metadata/metadata.json"
manager = CharacterManager(base_path, metadata_file)

character = "character_1"
asset_type = "eyes"
asset_sub_type = "shock"
# exta = {"name":"a_e_h"} # for mouth
# extra = {"name":"angry_M"} # for normal eyes
extra = {"name": "shock_R", "blink": False}  # for normal eyes

image, metadata = manager.get_asset(character, asset_type, asset_sub_type, extra)
print(f"Loaded {extra} with metadata: {metadata}")
image.show()

# Additional functionality usage
# zoomed_image = manager.zoom_at(image, x=25, y=25, zoom=2)
# zoomed_image.show()

# bg_image = Image.new('RGBA', (200, 200), (255, 255, 255, 0))
# fg_image = image
# combined_image = manager.adding_image(bg_image, fg_image, location=(50, 50), size=50, rotation=45, mirror=True)
# combined_image.show()
