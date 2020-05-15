from marsh import marsh
from models.users import UserModel


class UserSchema(marsh.ModelSchema):
    class Meta:
        model = UserModel
        load_only = ("password",)
        dump_only = ("id",)