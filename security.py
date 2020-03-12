from werkzeug.security import safe_str_cmp
from models.users import UserModel

def authenticate(username, password):
    user = UserModel.find_by_username(username)
    # safe_str_cmp is the safe string compare, safer way than '==' Operator
    if user and safe_str_cmp(user.password, password):
        return user

def identity(payload):
    user_id = payload['identity']
    return UserModel.find_by_id(user_id)