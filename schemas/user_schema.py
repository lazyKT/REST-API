from marshmallow import Schema, fields


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    uuid = fields.Int(dump_only=True)
    email = fields.Str()
    username = fields.Str()
    password = fields.Str(load_only=True)
    role = fields.Str()
    profile_pic = fields.Str()
    status = fields.Str(dump_only=True)
    createdOn = fields.Str(dump_only=True)
    updatedOn = fields.Str(dump_only=True)