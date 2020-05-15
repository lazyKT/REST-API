import os
from dotenv import load_dotenv

from flask_restful import Api
from flask import Flask, render_template, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_uploads import configure_uploads, patch_request_class

from db import db
from marsh import marsh
import models.genre as genre
from models.users import UserModel
from resources.users import (UserRegister, User, UserLogin,
                             TokenRefresh, UserLogout, UserList, ChangePassword)
from resources.songs import Song, SongList
from resources.genres import Genre, GenreList
from resources.images import ImageUpload, Image
from lib.image_helper import IMAGE_SET

app = Flask(__name__)
load_dotenv(".env", verbose=True)
app.config.from_object("default_config")
app.config.from_envvar("APPLICATION_SETTINGS")
patch_request_class(app, 16 * 1024 * 1024)  # 16mb max size
configure_uploads(app, IMAGE_SET)
api = Api(app)
CORS(app)


# !!! Before the first request, as in very first start of the app, Create the REQUIRED DATABASE TABLES
@app.before_first_request
def create_database_tables():
    db.create_all()
    status_code = genre.import_data_from_json()
    log_txt = 'Data Initialization Finished! '
    result_txt = 'Data Created! -' if status_code == 0 else 'Data Already Existed!'
    app.logger.info(log_txt + result_txt + " Status Code - " + str(status_code))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


jwt = JWTManager(app)


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
        'error': "missing_token"
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


api.add_resource(Song, '/songs/<int:_id_>')
api.add_resource(SongList, '/songs')
api.add_resource(Genre, '/genre/<int:_id>')
api.add_resource(GenreList, '/genres')
api.add_resource(UserRegister, '/register')
api.add_resource(User, '/user/<int:user_id>')
api.add_resource(UserLogin, '/login')
api.add_resource(TokenRefresh, '/refresh')
api.add_resource(UserLogout, '/logout')
api.add_resource(UserList, '/users')
api.add_resource(ChangePassword, '/changepwd/<int:_id>')
api.add_resource(ImageUpload, "/upload/image")
api.add_resource(Image, "/img/<string:filename>")

# Main Program Here __main__
if __name__ == '__main__':
    db.init_app(app)
    marsh.init_app(app)
    app.run(port=8000)
