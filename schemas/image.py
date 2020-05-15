import typing
from marshmallow import Schema, fields
from werkzeug.datastructures import FileStorage

"""Validation the image sent by users"""


class FileStorageField(fields.Field):

    default_error_messages = {
        "invalid": "Not a Valid Image",
    }

    def _deserialize(self, value, attr, data, **kwargs):
        if value is None:
            return None
        if not isinstance(value, FileStorage):
            self.fail("invalid")
        return value


class ImageSchema(Schema):
    image = FileStorageField(required=True)
