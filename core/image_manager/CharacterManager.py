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
        # Get the original dimensions of the image
        w, h = img.size

        # Calculate the dimensions of the crop area
        crop_width = w / zoom
        crop_height = h / zoom

        # Calculate the coordinates of the top-left and bottom-right corners of the crop area
        left = max(x - crop_width / 2, 0)
        top = max(y - crop_height / 2, 0)
        right = min(x + crop_width / 2, w)
        bottom = min(y + crop_height / 2, h)

        # Crop the image
        img = img.crop((left, top, right, bottom))

        # Resize the cropped image back to the original size
        return img.resize((w, h), Image.LANCZOS)

    def adding_image(
        self,
        img_bg,
        img_fg,
        position,
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

        img_bg.paste(img_fg, position, mask=img_fg)

        return img_bg

    def mirror_image(self, img):
        return ImageOps.mirror(img)

    def adding_eyes_and_mouth(self, head, eye, mouth, eyes_metadata, mouth_metadata):

        new_image = self.adding_image(
            head,
            eye,
            position=eyes_metadata["position"],
            rotation=0,
            mirror=False,
            size_cordinates=eyes_metadata["size"],
        )

        new_image = self.adding_image(
            new_image,
            mouth,
            position=mouth_metadata["position"],
            mirror=True,
            size_cordinates=mouth_metadata["size"],
        )
        # if face_path[-5] == "R":
        #     new_image = mirror_image(new_image)
        return new_image

    def adding_head_and_body(self, head, body, metadata, rotation=0):

        new_image = self.adding_image(
            body,
            head,
            position=metadata["position"],
            rotation=rotation,
            mirror=False,
            size_cordinates=metadata["size"],
        )

        return new_image

    def adding_background(self, body, background, metadata, rotation=0, zoom=0):
        new_image = self.adding_image(
            background,
            body,
            position=metadata["position"],
            rotation=rotation,
            mirror=True,
            size_cordinates=metadata["size"],
        )

        if zoom > 0 and zoom < 8:
            print(metadata["zoom_point"])
            x = metadata["zoom_point"][0]
            y = metadata["zoom_point"][1]
            new_image = self.zoom_at(new_image, x, y, zoom)

        return new_image

    def get_character(
        self,
        Character,
        Emotion,
        Body,
        Head_Direction,
        Eyes_Direction,
        Background,
        Mouth_Emotion,
        Mouth_Name,
        zoom,
    ):
        # Head input
        # character = "character_1"
        # asset_type = "head"
        # asset_sub_type = "L"
        head, _ = self.get_asset(Character, "head", Head_Direction)

        # Eyes input
        eyes_name = {"name": Eyes_Direction}  # for normal eyes
        # eyes = {"name": "shock_R", "blink": True}  # for blinking
        eyes, eyes_metadata = self.get_asset(Character, "eyes", Emotion, eyes_name)

        # mouth
        mouth_name = {"name": Mouth_Name}
        mouth, mouth_metadata = self.get_asset(
            Character, "mouth", Mouth_Emotion, mouth_name
        )

        head = self.adding_eyes_and_mouth(
            head, eyes, mouth, eyes_metadata, mouth_metadata
        )

        # Body Input
        body, body_metadata = self.get_asset(Character, "body", Body)

        character = self.adding_head_and_body(
            body=body, head=head, metadata=body_metadata
        )

        # Background
        background, background_metadata = self.get_asset(
            Character, "background", Background
        )

        scean = self.adding_background(
            body=character,
            background=background,
            metadata=background_metadata,
            zoom=zoom,
        )
        return scean, background_metadata


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
