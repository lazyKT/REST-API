from dotenv import load_dotenv
from celery import Celery

from flask_restful import Api
from flask import Flask, render_template, jsonify, request, send_file
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask_cors import CORS
# !!! Werkzeug import in flask_uploads has been updated
# !!! import Secure_filename from werkzeug.utils and FileStorage from werkzeug.datastructures
from flask_uploads import configure_uploads, patch_request_class

from db import db
from marsh import marsh
from routes.pub import pub
from routes.email import mail
from routes.songs import song
from routes.users import __init_users_routes__

from models.songs import SongModel
from models.users import UserModel
from resources.users import (UserRegister, User, UserLogin,
                             TokenRefresh, UserLogout, UserList, ChangePassword, password_reset, password_forget)
from resources.songs import Song, SongList, add_song, get_song_resource, mysongs_list
from resources.images import ImageUpload, Image, AvatarUpload, Avatar

from lib.image_helper import IMAGE_SET
from lib.tokens import __init_jwt__
from lib.vdo_helper import convert_mp3, url_helper

def create_app():
    app = Flask(__name__)
    load_dotenv(".env", verbose=True) # Load the App Parameters and Const from .env
    app.config.from_object("default_config") 
    app.config.from_envvar("APPLICATION_SETTINGS")

    # Celery Configuations
    app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
    app.config['CELERY_RESULT_BACKEND'] = 'db+sqlite:///data.db'
    app.config['CELERY_TRACK_STARTED'] = True
    app.config['CELERY_SEND_EVENTS'] = True

    # Celery Initialization
    celery = Celery(app.name, 
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND'])
    celery.conf.update(app.config)

    patch_request_class(app, 16 * 1024 * 1024)  # 16mb max size
    configure_uploads(app, IMAGE_SET) # Load Configurations for the upload media
    api = Api(app) # Initialise the flask_restful
    CORS(app) # Initialise CORS
    __init_jwt__(app) # Initialise JWT instance

    # !!! Before the first request, as in very first start of the app, Create the REQUIRED DATABASE TABLES
    @app.before_first_request
    def create_database_tables():
        db.create_all()
        """ : Genre is currently left out from API, may be used in tbe Future. """
    

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
    """ : Registering Blueprints """
    app.register_blueprint(pub)
    app.register_blueprint(mail)
    app.register_blueprint(song)

    __init_users_routes__(api)


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
    @app.route('/process', methods=['GET','POST'])
    @jwt_required
    def process():
        if request.method == 'GET':
            return render_template('process.html')
        data = request.get_json()
        # url_helper function helps to validate the url and remove the playlist information from url
        # : for example, if a user request a song from youtube playlist, only the song requested will be processed,
        # : removing playlist id from url. This is being done because of Youtube-dl feature.
        # : Youtube-dl converts all the songs from playlist if the url contain playlist id
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
        
    
    # Routes and Resources
    api.add_resource(Song, '/songs/<int:_id_>')
    api.add_resource(SongList, '/songs')
    

    db.init_app(app)
    marsh.init_app(app)
    app.run()

    return app
