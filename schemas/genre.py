from marshmallow import Schema, fields


class GenreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()
    url = fields.Str()
