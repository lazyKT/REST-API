from marshmallow import Schema, fields


class SongSchema(Schema):
    id = fields.Int(dump_only=True)
    # task_id = fields.Str()
    title = fields.Str()
    posted_by = fields.Int()
    url = fields.Str()
