from marshmallow import Schema, fields, validate

class UserSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(max=80))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6, max=128))  # Optional: Set max length for password

class BoardSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(max=80))
    description = fields.Str(validate=validate.Length(max=256))  # Optional: You can also validate non-empty descriptions if necessary

class ThreadSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(max=128))
    board_id = fields.Int(required=True)
    description = fields.Str(required=True, validate=[validate.Length(min=1), validate.Length(max=500)])  # Adding max length for description
