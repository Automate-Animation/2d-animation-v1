import os
import json
from PIL import Image, ImageOps
import statistics
import numpy as np
import random


class CharacterManager:
    def __init__(self, base_path, metadata_file):
        self.base_path = base_path
        self.metadata = self.load_metadata(metadata_file)

    def load_metadata(self, metadata_file):
        with open(metadata_file, "r") as file:
            return json.load(file)

    def get_image_path(self, character, asset_type, asset_name):
        return os.path.join(self.base_path, character, asset_type, f"{asset_name}.png")

    def get_random_png_file_name(self, character, asset_type, asset_sub_type):

        full_path = os.path.join(self.base_path, character, asset_type, asset_sub_type)

        png_files = [f for f in os.listdir(full_path) if f.endswith(".png")]

        if not png_files:
            return None

        selected_file = random.choice(png_files)

        return os.path.splitext(selected_file)[0]

    def get_character_asset_path(
        self, character, asset_type, asset_sub_type, asset_name
    ):
        return os.path.join(
            self.base_path, character, asset_type, asset_sub_type, f"{asset_name}.png"
        )

    def get_eyes_blinking_asset_path(
        self, character, asset_type, asset_sub_type, blink_file, asset_name
    ):
        return os.path.join(
            self.base_path,
            character,
            asset_type,
            asset_sub_type,
            blink_file,
            f"{asset_name}.png",
        )

    def get_asset_metadata(self, character, asset_type, asset_name):
        return self.metadata[character][asset_type][asset_name]

    def load_image(self, character, asset_type=None, asset_sub_type=None, extra={}):
        if asset_type == "body" or asset_type == "background" or asset_type == "head":
            print(character, asset_type)
            asset_name = self.get_random_png_file_name(
                character, asset_type, asset_sub_type
            )
            image_path = self.get_character_asset_path(
                character, asset_type, asset_sub_type, asset_name
            )
        elif asset_type == "mouth":
            asset_name = extra.get("name", None)
            image_path = self.get_character_asset_path(
                character, asset_type, asset_sub_type, asset_name
            )
        elif asset_type == "eyes":
            asset_name = extra.get("name", None)
            blink = extra.get("blink", False)
            blink_file = asset_sub_type + "_blink"
            if (
                blink
            ):  # reason for separate cuz of blinking of images are in different folder
                image_path = self.get_eyes_blinking_asset_path(
                    character, asset_type, asset_sub_type, blink_file, asset_name
                )
            else:
                image_path = self.get_character_asset_path(
                    character, asset_type, asset_sub_type, asset_name
                )

            asset_name = asset_sub_type

        return Image.open(image_path), asset_name

    def get_asset(self, character, asset_type, asset_sub_type, extra={}):
        image, asset_name = self.load_image(
            character, asset_type, asset_sub_type, extra
        )
        if asset_type != "head":
            metadata = self.get_asset_metadata(character, asset_type, asset_name)
        else:
            metadata = None
        return image, metadata

    def zoom_at(self, img, x, y, zoom):
        w, h = img.size
        zoom2 = zoom * 2
        img = img.crop((x - w / zoom2, y - h / zoom2, x + w / zoom2, y + h / zoom2))
        return img.resize((w, h), Image.LANCZOS)

    def adding_image(
        self,
        img_bg,
        img_fg,
        location,
        size=30,
        rotation=0,
        mirror=False,
        size_cordinates=None,
    ):
        """PIL import image required not openCV. this function is responsible for adding image, size and rotating it"""
        if size_cordinates is not None:
            dim = size_cordinates
        else:
            width, height = img_fg.size
            scale_percent = size  # percent of original size
            width = int(width * scale_percent / 100)
            height = int(height * scale_percent / 100)
            dim = (width, height)

        if mirror:
            img_fg = ImageOps.mirror(img_fg)

        if rotation != 0:
            img_fg = img_fg.rotate(rotation)

        img_fg = img_fg.resize(dim)

        img_bg.paste(img_fg, location, mask=img_fg)

        return img_bg

    def mirror_image(self, img):
        return ImageOps.mirror(img)


# Example usage
# base_path = (
#     "/home/oye/Documents/animation_software/2d-animation-v1/core/images/characters"
# )
# metadata_file = "/home/oye/Documents/animation_software/2d-animation-v1/core/images/metadata/metadata.json"
# manager = CharacterManager(base_path, metadata_file)

# character = "character_1"
# asset_type = "eyes"
# asset_sub_type = "shock"
# # exta = {"name":"a_e_h"} # for mouth
# # extra = {"name":"angry_M"} # for normal eyes
# extra = {"name": "shock_R", "blink": False}  # for normal eyes

# image, metadata = manager.get_asset(character, asset_type, asset_sub_type, extra)
# print(f"Loaded {extra} with metadata: {metadata}")
# image.show()

# # Additional functionality usage
# zoomed_image = manager.zoom_at(image, x=25, y=25, zoom=2)
# zoomed_image.show()

# bg_image = Image.new('RGBA', (200, 200), (255, 255, 255, 0))
# fg_image = image
# combined_image = manager.adding_image(bg_image, fg_image, location=(50, 50), size=50, rotation=45, mirror=True)
# combined_image.show()
