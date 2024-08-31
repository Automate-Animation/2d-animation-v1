from jsonschema import validate, ValidationError, SchemaError


from marshmallow import Schema, fields


class TextSchema(Schema):
    start = fields.Integer(required=True)
    end = fields.Integer(required=True)


class HeadDirectionSchema(Schema):
    text = fields.Nested(TextSchema, required=True)
    head_direction = fields.String(
        required=True, validate=lambda x: x in ["L", "R", "M"]
    )


class EyesDirectionSchema(Schema):
    text = fields.Nested(TextSchema, required=True)
    eyes_direction = fields.String(
        required=True, validate=lambda x: x in ["L", "R", "M"]
    )


class CharacterSchema(Schema):
    text = fields.Nested(TextSchema, required=True)
    character = fields.Integer(required=True)


class EmotionSchema(Schema):
    text = fields.Nested(TextSchema, required=True)
    emotion = fields.Integer(required=True)


class BodyActionSchema(Schema):
    text = fields.Nested(TextSchema, required=True)
    body_action = fields.Integer(required=True)


class IntensitySchema(Schema):
    text = fields.Nested(TextSchema, required=True)
    intensity = fields.Integer(required=True)


class ZoomSchema(Schema):
    text = fields.Nested(TextSchema, required=True)
    zoom = fields.Integer(required=True)


class ScreenModeSchema(Schema):
    text = fields.Nested(TextSchema, required=True)
    screen_mode = fields.Integer(required=True)


from marshmallow import ValidationError


def validate_data(data, schema):
    try:
        result = schema.load(data)
        # print("Valid data:", result)
        return True, "Valid data"
    except ValidationError as err:
        print("Validation errors:", err.messages)
        return False, "Validation errors:" + str(err.messages)


# Example usage
# data = [{'text': {'start': 0, 'end': 81}, 'character': None}]
# schema = CharacterSchema(many=True)
# validate_data(data, schema)
