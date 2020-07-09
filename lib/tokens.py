"""
: This is JWT initialization and implementation
"""
from flask import jsonify
from flask_jwt_extended import JWTManager

from models.users import UserModel

def __init_jwt__(app):
    # Initialise JWT with app configuration
    jwt = JWTManager(app)

    """
    : JWT Tokens Responses and Handlers
    """
    @jwt.user_claims_loader
    def add_claims_to_jwt(identity):  # !!! identity comes from access_token
        user = UserModel.find_by_id(identity)

        if user and user.role == "admin":
            return {'is_admin': True}

        return {'is_admin': False}


    @jwt.token_in_blacklist_loader
    def check_if_token_in_blacklist(decrypted_token):
        return decrypted_token['jti'] in UserModel.BLACKLIST


    """Error Handling Upon Token Operations"""


    @jwt.expired_token_loader  # !!! Feed Back to users upon expired token
    def expired_token_callback():
        return jsonify({
            'msg': "The Token had expired!",
            'error': "token_expired"
        }), 401


    @jwt.invalid_token_loader  # !!! Feed Back to users upon invalid token
    def invalid_token_callback(error):
        return jsonify({
            'msg': str(error)
        }), 401


    @jwt.unauthorized_loader  # !!! Request without JWT Tokens
    def missing_token_callback(error):
        return jsonify({
            'msg': "Missing Valid Token!!",
            'error': error
        }), 401


    @jwt.needs_fresh_token_loader  # !!! Require JWT Tokens
    def token_not_fresh_callback():
        return jsonify({
            'msg': "Token needs to be refreshed",
            'error': "fresh_token_required"
        }), 401


    @jwt.revoked_token_loader  # !!! Token Revoking/ Logout
    def revoked_token():
        return jsonify({
            'msg': "Token has been revoked",
            'error': "revoked_token"
        }), 401
