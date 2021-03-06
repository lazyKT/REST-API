from dotenv import load_dotenv
from celery import Celery
import os

from flask_restful import Api
from flask import Flask, render_template, jsonify, request, send_file, flash
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, get_raw_jwt
from flask_cors import CORS
# !!! Werkzeug import in flask_uploads has been updated
# !!! import Secure_filename from werkzeug.utils and FileStorage from werkzeug.datastructures
from flask_uploads import configure_uploads, patch_request_class

from db import db
from marsh import marsh
from models.songs import SongModel
from models.users import UserModel
from resources.users import (UserRegister, User, UserLogin,
                             TokenRefresh, UserLogout, UserList, ChangePassword, password_reset, password_forget)
from resources.songs import Song, SongList, add_song, get_song_resource, mysongs_list
from resources.images import ImageUpload, Image, AvatarUpload, Avatar
from lib.image_helper import IMAGE_SET
from lib.vdo_helper import convert_mp3, find_file, url_helper
from lib.link_token import confirm_token, generate_link_token
from lib.utils import validate_requests
from lib.email_helper import send_report, send

app = Flask(__name__)
load_dotenv(".env", verbose=True) # Load the App Parameters and Const from .env
app.config.from_object("default_config")    
app.config.from_envvar("APPLICATION_SETTINGS")

# Celery Configuations
app.config['CELERY_BROKER_URL'] = os.environ.get('CELERY_BROKER_URL')
app.config['CELERY_RESULT_BACKEND'] = os.environ.get('DATABASE_URL')
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
    """ : Genre is currently left out from API, may be used in tbe Future. """
    # status_code = genre.import_data_from_json()
    # log_txt = 'Data Initialization Finished! '
    # result_txt = 'Data Created! -' if status_code == 0 else 'Data Already Existed!'
    # app.logger.info(log_txt + result_txt + " Status Code - " + str(status_code))



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
    print(request.headers)
    return render_template('about.html')

# This route is for contact to site admin about help and bug report
@app.route('/help', methods=['POST'])
def help():
    print('From', request.form['from'])
    print('to', request.form['to'])
    print('subject', request.form['subject'])
    print('Body', request.form['text'])
    return ''
   # subject = request.get_json()['subject']
   # issue = request.get_json()['issue']
   # email = request.get_json()['email']
   # try:
   #     send_report(email, subject, issue)
   #     return "Success"
   # except:
   #     return "Failed"


# This is a route for the users report and feedback
@app.route('/report', methods=['POST'])
def report():
    print(request.get_json())
    title = request.get_json()['title']
    subject = request.get_json()['subject']
    email = request.get_json()['email']
    report_type = request.get_json()['type']
    try:
        print("before sending report")
        # Forwarding issue to the admin's email address
        send_report(email, title, subject, report_type)
        # Reply an email to user that the admin has received the report
        # print("Replying email")
        body = render_template('do_not_reply.html', issue= subject, report_type=report_type)
        send(None, email, "[MusiCloud]: Do Not Reply", body)
        return "Success", 200
    except:
        return "Failed", 500



"""
: This is helper route to convert the Youtube Video to MP3 with the help of Youtube_dl.
: The process function takes the Request object from user and perform the convertion of video to mp3
: To prevent unnecessary delay and overhead on Server, the convertion process will be executed on different thread.
: The process will be handed over to redis worker for Execution, with the help of Celery.
: This function will not wait the execution of CONVERTION process. 
: The function will response back to user just after it has sent the CONVERTION task to redis worker
: In order to perform an operation with this route, 
: SSL Certificate must be installed and updated: $ pip install --upgrade Certifi
: Ffmpeg must be installed. Learn more about ffmpeg @  https://www.ffmpeg.org/about.html
"""
@app.route('/process', methods=['POST'])
@jwt_required
def process():
    data = request.get_json()
    # url_helper function helps to validate the url and remove the playlist information from url
    # : for example, if a user request a song from youtube playlist, only the song requested will be processed,
    # : removing playlist id from url. This is being done because of Youtube-dl feature.
    # : Youtube-dl converts all the songs from playlist if the url contain playlist id
    if data is None:
        return { 'msg': 'Empty Request' }, 400
    url = url_helper(data['url'])
    # : If url is invalid, url_helper function will return None. Then we give 'Invalid url response' to client side.
    if url is None:
        return {'msg': "Invalid URL. Please check again!"}, 400
    # if url is already exists in Song DB, just save the song with user_id, instead of creating again
    if SongModel.find_by_url(url):
        new_song = add_song(data)
        return new_song
    convertion = task.delay(url)
    result = add_song(data, convertion.id) # DB Operation
    return result


"""
: This is a helper route that the client can request the list of songs that a user converted.
: This route will receive the user id from requested url, then
: it will response the list of songs that is related to user id.
"""
@app.route('/mysongs', methods=['GET'])
@jwt_required
def mysongs():
    user_id = get_jwt_identity()
    try:
        return mysongs_list(user_id)
    except Exception as e:
        print(type(e))
        return str(e), 404
    


"""
: This route allows the client side to get the song to play.
: The basic concept is that the client side request a song with song id. This function takes the song id as an input.
: And it returns the actual mp3 file of the song.
: If file exists, return status_code 200 along with the file_path for client-side to access.
: If file doesn't exist, return status_code 404, with the message, "File Not Found"
"""
@app.route('/listen/<song_id>')
def listen_song(song_id):
    # wrong at get_song_resource NEED TO FIXED BY TOMORROW
    file_name = get_song_resource(song_id)
    print("file_name{file_name}")
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
@jwt_required
def get_status(task_id):
    try:
        from resources.songs import check_task_status
        return check_task_status(task_id)
    except:
        return {'msg': "Error! Requested Resources Not Available!"}, 400


"""
: This is a route for the user confirmation.
: This route is sent to user's email address after succesful registeration.
: Users must click this route in their email inbox to activate their account.
: InActive users cannot be validated and cannot access the app.
"""
@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        return "The Confirmation Link has been invalid or expired."
    if not email:
        return "The Confirmation Link has been expired.\nIf you account has not confirmed yet, try to log in to get confirmation link"
    user = UserModel.find_by_email(email)
    if not user:
        return "User Not Found"
    if user.status == "Active":
        return "Your account already confirmed and active."
    else:
        UserModel.activate_account(user.id)
        return render_template('activate.html')


"""
: This route is for the activation of the account for the deactivated users.
: The deactivated users can refer to this route to re-activate their account with their email addresses.
"""
@app.route('/re-activate', methods=['POST'])
def activate_account():
    user = UserModel.find_by_email(request.get_json()['email'])
    if not user:
        return {'msg': "User account related to this email address, is not found."}, 404
    token = generate_link_token(user.email)
    UserModel.send_confirmation_email(token, user.email, user.username)
    return {'msg': "An Activation Link has been sent to your email Address."}, 200


"""
: This is a route to deactivate the account.
: Users can deactivate the account by sending this route.
"""
@app.route('/deactivate/<username>')
@jwt_required
def deactivate_account(username):
    user = UserModel.find_by_username(username)
    UserModel.deactivate_account(user.id)
    return {'msg': "Account Deactivated!"}, 200


"""
: This route is to request the password reset link when users forgot their password at login.
"""
@app.route('/forget-password', methods=['POST'])
def forget_password():
    try:
        email = request.get_json()['email']
        res = password_forget(email)
        return res
    except:
        return {'msg': "Key-Error 'email'"}, 400


"""
: Password Reset Link.
: This route is the password reset link for users who forgot their passwords on Login Page
: Users click 'Forgot Password?' link and the route link will be sent to their emails.
"""
@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = confirm_token(token, expiration=600) # ! expired in 10 minutes
    except:
        return "The reset-password link is invalid or expired."
    if not email:
        return "The reset-password link is expired. Try to request new one."
    user = UserModel.find_by_email(email)
    if user and request.method == 'GET':
        return render_template('reset_pwd.html', username = user.username)
    if request.form['reset'] == 'Reset':
        if request.form['password'] == request.form['confirm_pwd']:
            password = request.form['password']
            return password_reset(user.id, password)
        else: # If passwords doesn't match. Alert User
            flash("Passwords don't match!")
            return render_template('reset_pwd.html', username = user.username)

"""
: This is a route for a logout from API
: This route terminates the access to the API for the requests coming to it
: by adding the access token into JWT Blacklist
"""
@app.route('/logout', methods=['POST'])
@jwt_required
def logout():
    print("Logging Out ...")
    jti = get_raw_jwt()['jti']
    UserModel.BLACKLIST.add(jti)
    return {'msg': 'Successfully Log Out'}, 200


# Routes and Resources
api.add_resource(Song, '/songs/<int:_id_>')
api.add_resource(SongList, '/songs')
api.add_resource(UserRegister, '/register')
api.add_resource(User, '/user/<int:user_id>')
api.add_resource(UserLogin, '/login')
api.add_resource(TokenRefresh, '/refresh')
# api.add_resource(UserLogout, '/logout')
api.add_resource(UserList, '/users')
api.add_resource(ChangePassword, '/changepwd/<int:_id>')
api.add_resource(ImageUpload, "/upload/image") # Upload Image
api.add_resource(Image, "/img/<string:filename>") # Fetch Uploaded Image by Name
api.add_resource(AvatarUpload, "/upload/avatar") # Upload User Profile Avatar
api.add_resource(Avatar, "/avatar/<int:_id_>") # Fetch User Profile Avatar by User ID

db.init_app(app)
marsh.init_app(app)

# Main Program Here __main__
if __name__ == '__main__':
    app.run()
