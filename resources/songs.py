from flask_restful import Resource
from flask_jwt_extended import (
    jwt_required,
    get_jwt_claims
)
from flask import request, send_file, jsonify
from marshmallow import ValidationError
from schemas.songs import SongSchema
from models.songs import SongModel
from models.users import UserModel
from __wrappers__ import is_admin
from lib.vdo_helper import url_helper
from lib.utils import response_builder

song_schema = SongSchema()


class Song(Resource):

    @classmethod
    @jwt_required
    def get(cls, _id_):
        song = SongModel.find_by_id(_id_)
        if song:
            return song.json(), 200
        return {'msg': 'Song Not Exists'}

    @classmethod
    @jwt_required
    @is_admin
    def delete(cls, _id_):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'msg': "Admin Privilege Required."}, 401
        song = SongModel.find_by_id(_id_)
        if song:
            song.delete_from_db()
            return {'msg': 'Song deleted successfully!!'}, 200
            # return {'msg': 'Unsuccessful Operation!'}, 400
        return {'msg': "Song Not Exists!"}, 400

    @classmethod
    @jwt_required
    @is_admin
    def put(cls, _id_):
        song = SongModel.find_by_id(_id_)
        if not song:
            return {"msg": "Invalid Song. Doesn't exist!!"}, 400
        try:
            song_data = song_schema.load(request.get_json())
            song.update_song(_id_, song_data)
            return song.json(), 200
        except ValidationError as err:
            return err.messages, 400
        except:
            return {'msg': "Error Performing Request!"}, 500


class SongList(Resource):

    @classmethod
    def get(cls):
        songs = [song() for song in SongModel.query.all()]
        return songs

    @classmethod
    # @fresh_jwt_required  # !!! Token must be fresh in order to post a song
    def post(cls):
        try:
            song_data = song_schema.load(request.get_json())
            new_song = SongModel(**song_data)
            new_song.save_to_db()
            return new_song(), 201
        except ValidationError as err:
            return err.messages, 400
        except:
            return {'msg': "Error Performing Request!"}, 500


"""
 ! : This is a helper function for the DB Operation of /process route.
 : After the convertion process has been passed to redis worker, this function will be executed
 : Take the task id from redis worker and save the task_id along with the requests obj in DB
"""
def add_song(req, task_id='existed_101'):

    # : Validate url
    url = url_helper(req['url'])
    if url is None:
        return {'msg': "Invalid URL. Please check again!"}, 400
    
    if SongModel.check_duplication(req['posted_by'], req['url']):
        return response_builder(status_code=400, body="Song Exists")

    try:
        # Save song info into DB
        new_song = SongModel(task_id, req['title'], req['posted_by'], req['genre_id'], url)
        new_song.save_to_db()
        return new_song(), 201
    except:
        return "Error on SongModel Instance", 500

"""
: This is a helper function for the route "/listen/<song_id>".
: This function takes song id as an input parameter and return the mp3 file name related to the song
"""
def get_song_resource(song_id):
    song = SongModel.find_by_id(song_id)
    if song:
        song_url = song.url
        song_name = song_url.split("=")[1]
        return song_name
    return "Song Not Exists"


"""
: This is a helper function for the route, '/mp3Convert/status'
: After adding a new song request and the convertion to mp3 process is being sent to Celery Worker,
: the client-side needs to check the status and updates of the convertion process.
: This function checks the status and updates of the process and response the status back to the client-side.
: This function will normally check the task-id in Celery-Task DB Table for the status. 
: There are two statoos availble, success and failure.
: If error: reponse 500. If success: response 201. If task not found, response "on-progress": 200
"""
def check_task_status(task_id):
    try:
        from models.task import get_status
        task = get_status(task_id)
        print(task)
        if task:
            if task.status == "SUCCESS":
                return response_builder(status_code=201, body='Your Song is Ready to Play')
            else:
                return response_builder(status_code=500, body='Internal Server Error')
        return response_builder(status_code=200, body='On-Progress')
    except:
        return response_builder(status_code=400, body='Bad Request')


"""
: This is a helper function for the route '/mysongs/<user_id>'.
: This function return the list of songs related to user id after checking the user validity.
"""
def mysongs_list(user_id):
    if not UserModel.find_by_id(user_id):
        raise Exception('User Not found!!')
    songs = [song() for song in SongModel.find_by_user(user_id)]
    if not songs:
        return response_builder(status_code=404, body="Empty!!")
    print(type(songs))
    return response_builder(status_code=200, body=songs)
