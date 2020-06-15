from dotenv import load_dotenv
from celery import Celery

from flask_restful import Api
from flask import Flask, render_template, jsonify, request
from flask_jwt_extended import JWTManager
from flask_cors import CORS
# !!! Werkzeug import in flask_uploads has been updated
# !!! import Secure_filename from werkzeug.utils and FileStorage from werkzeug.datastructures
from flask_uploads import configure_uploads, patch_request_class

from db import db
from marsh import marsh
import models.genre as genre
from models.users import UserModel
from resources.users import (UserRegister, User, UserLogin,
                             TokenRefresh, UserLogout, UserList, ChangePassword)
from resources.songs import Song, SongList, add_song
from resources.genres import Genre, GenreList
from resources.images import ImageUpload, Image, AvatarUpload, Avatar
from lib.image_helper import IMAGE_SET
from lib.vdo_helper import convert_mp3

app = Flask(__name__)
load_dotenv(".env", verbose=True) # Load the App Parameters and Const from .env
app.config.from_object("default_config") 
app.config.from_envvar("APPLICATION_SETTINGS")

# Celery Configuations
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'db+sqlite:///data.db'
# app.config['CELERY_RESULT_DBURI'] = 'sqlite:///data.db'
app.config['CELERY_TRACK_STARTED'] = True
app.config['CELERY_SEND_EVENTS'] = True

# Celery Initialization
celery = Celery(app.name, 
    broker=app.config['CELERY_BROKER_URL'],
    backend=app.config['CELERY_RESULT_BACKEND'])
celery.conf.update(app.config)

patch_request_class(app, 16 * 1024 * 1024)  # 16mb max size
configure_uploads(app, IMAGE_SET) # Load Configurations for the upload media
api = Api(app)
CORS(app)


# Celery Task
@celery.task
def task(url):
    print("Start Execution...")
    convert_mp3(url)
    print("Finished Execution...")
    return url.split('=')[1]


# !!! Before the first request, as in very first start of the app, Create the REQUIRED DATABASE TABLES
@app.before_first_request
def create_database_tables():
    db.create_all()
    status_code = genre.import_data_from_json()
    log_txt = 'Data Initialization Finished! '
    result_txt = 'Data Created! -' if status_code == 0 else 'Data Already Existed!'
    app.logger.info(log_txt + result_txt + " Status Code - " + str(status_code))


# static routes
@app.route('/')
def index():
    return "Hello Flask"


@app.route('/process', methods=['GET','POST'])
def process():
    if request.method == 'GET':
        return render_template('process.html')
    # if request.form['submit'] == 'Convert':
    #     url = request.form['url']
    #     # result = task.delay(url)
    #     add_song(request)
    #     return f"{url} with has been sent to Celery!"
    data = request.get_json()
    convertion = task.delay(data['url'])
    result = add_song(data, convertion.id)
    return result


@app.route('/about')
def about():
    return render_template('about.html')


# Initialise JWT with app configuration
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


# Routes and Resources
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
api.add_resource(ImageUpload, "/upload/image") # Upload Image
api.add_resource(Image, "/img/<string:filename>") # Fetch Uploaded Image by Name
api.add_resource(AvatarUpload, "/upload/avatar") # Upload User Profile Avatar
api.add_resource(Avatar, "/avatar/<int:_id_>") # Fetch User Profile Avatar by User ID

# Main Program Here __main__
if __name__ == '__main__':
    db.init_app(app)
    marsh.init_app(app)
    app.run(port=8000)
