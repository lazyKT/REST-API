from flask import Blueprint, send_file
from flask_jwt_extended import get_jwt_identity, jwt_required

from resources.songs import get_song_resource, mysongs_list, Song, SongList

from lib.vdo_helper import find_file

# Blueprint Initialization
song = Blueprint('song', __name__)


"""
: This route allows the client side to get the song to play.
: The basic concept is that the client side request a song with song id. This function takes the song id as an input.
: And it returns the actual mp3 file of the song.
: If file exists, return status_code 200 along with the file_path for client-side to access.
: If file doesn't exist, return status_code 404, with the message, "File Not Found"
"""
@song.route('/listen/<song_id>')
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
@song.route('/mp3Convert/status/<task_id>')
@jwt_required
def get_status(task_id):
    try:
        from resources.songs import check_task_status
        return check_task_status(task_id)
    except:
        return {'msg': "Error! Requested Resources Not Available!"}, 400


"""
: This is a helper route that the client can request the list of songs that a user converted.
: This route will receive the user id from requested url, then
: it will response the list of songs that is related to user id.
"""
@song.route('/mysongs', methods=['GET'])
@jwt_required
def mysongs():
    user_id = get_jwt_identity()
    try:
        return mysongs_list(user_id)
    except Exception as e:
        print(type(e))
        return str(e), 404

""" -- Routes of Songs using FlaskRestful -- """
def __init_song_routes__(api):
    api.add_resource(Song, '/songs/<int:_id_>')
    api.add_resource(SongList, '/songs')