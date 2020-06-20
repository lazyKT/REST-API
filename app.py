from dotenv import load_dotenv
from celery import Celery

from flask_restful import Api
from flask import Flask, render_template, jsonify, request, send_file
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
                             TokenRefresh, UserLogout, UserList, ChangePassword, forget_password)
from resources.songs import Song, SongList, add_song, get_song_resource
from resources.genres import Genre, GenreList
from resources.images import ImageUpload, Image, AvatarUpload, Avatar
from lib.image_helper import IMAGE_SET
from lib.vdo_helper import convert_mp3, find_file

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

# Initialise JWT with app configuration
jwt = JWTManager(app)



# !!! Before the first request, as in very first start of the app, Create the REQUIRED DATABASE TABLES
@app.before_first_request
def create_database_tables():
    db.create_all()
    status_code = genre.import_data_from_json()
    log_txt = 'Data Initialization Finished! '
    result_txt = 'Data Created! -' if status_code == 0 else 'Data Already Existed!'
    app.logger.info(log_txt + result_txt + " Status Code - " + str(status_code))



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



"""
: ! Celery task which will be executed by redis worker
: This function takes a video-url (youtube) and convert the video into mp3
: The function only accepts Youtube Url
: To reduce the overhead on the server, playlists url are not allowed to pass in
: For the conversion of multiple videos, his function must be execute multiple times.
: If non-youtube or invalid url has been passed, it will not perform any conversion process-
: straight away return "Invalid URL"
"""
@celery.task
def task(url):
    if 'youtube.com' in url and '=' in url:
        print("Start Execution...")
        convert_mp3(url)
        print("Finished Execution...")
        return url.split('=')[1]
    return "Invalid Url"


# static routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

"""
: This is helper route to convert the Youtube Video to MP3 with the help of Youtube_dl.
: The process function takes the Request object from user and perform the convertion of video to mp3
: To prevent unnecessary delay and overhead on Server, the convertion process will be executed on different thread.
: The process will be handed over to redis worker for Execution, with the help of Celery.
: This function will not wait the execution of CONVERTION process. 
: The function will response back to user just after it has sent the CONVERTION task to redis worker
: In order to perform an operation with this route, 
: SSL Certificate must be installed and updated: $ pip install --upgrade Certi
: Ffmpeg must be installed. Learn more about ffmpeg @  https://www.ffmpeg.org/about.html
"""
@app.route('/process', methods=['GET','POST'])
def process():
    if request.method == 'GET':
        return render_template('process.html')
    data = request.get_json()
    url = data['url']
    if "youtube.com" in url and "=" in url:
        convertion = task.delay(data['url'])
        result = add_song(data, convertion.id) # DB Operation
        return result
    return {'msg': "Invalid URL. Please check again!"}, 400

"""
: This route allows the client side to get the song to play.
: The basic concept is that the client side request a song with song id. This function takes the song id as an input.
: And it returns the actual mp3 file of the song.
: If file exists, return status_code 200 along with the file_path for client-side to access.
: If file doesn't exist, return status_code 404, with the message, "File Not Found"
"""
@app.route('/listen/<song_id>')
def listen_song(song_id):
    file_name = get_song_resource(song_id)
    try:
        return send_file(find_file(file_name))
    except:
        return {'msg' : "Song Not Found!!"}, 404


"""
: This route allows the client-side to check the status of the convertion process
; After the client-side has successfully post add-new-song request, it will check the status and updates of the convertion
: The get_status function returns 3 responses. Each response at one time.
: 201: Successful Convertion. 200: Task On-Progress. 500: Failure
"""
@app.route('/mp3Convert/status/<task_id>')
def get_status(task_id):
    try:
        from resources.Song import check_task_status
        return check_task_status(task_id)
    except:
        return {'msg': "Error! Requested Resources Not Available!"}, 400

"""
: This is a route for the user confirmation.
: This route is sent to user's email address after succesful registeration.
: Users must click this route in their email inbox to activate their account.
: InActive users cannot be validated and cannot access the app.
"""
@app.route('/activate/<user_id>')
def confirm_user(user_id):
    UserModel.activate_account(user_id)
    return render_template('activate.html')


"""
: This route is for the activation of the account for the deactivated users.
: The deactivated users can refer to this route to re-activate their account with their email addresses.
"""
@app.route('/re-activate', methods=['POST'])
def activate_account():
    user = UserModel.find_by_email(request.get_json()['email'])
    user.send_confirmation_email()
    return {'msg': "An Activation Link has been sent to your email Address."}, 200

"""
: This is a route to deactivate the account.
: Users can deactivate the account by sending this route.
"""
@app.route('/deactivate/<username>')
def deactivate_account(username):
    user = UserModel.find_by_username(username)
    UserModel.deactivate_account(user.id)
    return {'msg': "Account Deactivated!"}, 200

"""
: Password Reset Link.
: This route is the password reset link for users who forgot their passwords on Login Page
: Users click 'Forgot Password?' link and the route link will be sent to their emails.
"""
@app.route('/reset-password/<user_id>', methods=['GET', 'POST'])
def reset_password(user_id):
    if request.method == 'GET':
        return render_template('reset_pwd.html')
    if request.form['reset'] == 'Reset':
        password = request.form['password']

        return forget_password(user_id, password)


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
