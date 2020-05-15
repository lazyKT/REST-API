from marshmallow import Schema, fields


class SongSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    posted_by = fields.Int()
    url = fields.Str()
    genre_id = fields.Int()
