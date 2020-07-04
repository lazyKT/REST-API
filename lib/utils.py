import os
from flask import request
from functools import wraps
from flask_jwt_extended import get_jwt_claims
from werkzeug.security import safe_str_cmp


# Custom response builder for conversion of the song
# 201: created, 400: invalid url or request, 500: internal server error
def response_builder(status_code=401, body=None):
    return dict(status=status_code, msg=body)


# Before processing any requests, this function will check the authentication header inside incoming requests
# If the authentication value inside requests mathes 'APP.SECRET_KEY', allow the requests. If not deny!
# This function also validate the incoming requests, if required credentials or fields is missing, deny the requests
def validate_requests(f: object) -> object:
    @wraps(f)
    def validate(*args, **kwargs):
        secret = os.environ.get('SECRET_KEY')
        try:
            provided_secret = request.headers.get('x-api-key')
            if safe_str_cmp(provided_secret, secret):
                print(provided_secret+" equals")
                return f(*args, **kwargs)
            return response_builder(body="Unauthorized Access! Permission Denied"), 401
        except:
            return response_builder(body="Error Loading Request Credentials"), 401
    return validate


# !!! Check if the user has admin previllages
def is_admin(f: object) -> object:
    @wraps(f)
    def check(*args, **kwargs):
        if get_jwt_claims()["is_admin"]:
            return f(*args, **kwargs) 
        else: 
            return {'msg': "Unauthorized Access!"}, 401
    return check
