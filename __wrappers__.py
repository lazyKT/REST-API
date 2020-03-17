from functools import wraps
from flask_jwt_extended import get_jwt_claims

# !!! Check if the user has admin previllages
def is_admin(f):
    @wraps(f)
    def check(*args, **kwargs):
        if get_jwt_claims()["is_admin"]:
            return f(*args, **kwargs) 
        else: 
            return {'msg': "Unauthorized Access!"}, 401
    return check


