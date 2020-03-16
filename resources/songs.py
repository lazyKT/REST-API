from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    jwt_required, 
    get_jwt_claims, 
    jwt_optional, 
    get_jwt_identity, 
    fresh_jwt_required
)
import json
from models.songs import SongModel


class Song(Resource):

    # initiate reqparse which is similar to Patch
    # request parsing, validate the payload
    parser = reqparse.RequestParser()
    parser.add_argument('title', required=True, help="This field cannot be empty!")
    parser.add_argument('artist',required=True,help="This field cannot be empty!")
    parser.add_argument('genre_id',type=int,required=True,help="Song must have genre!")

    @jwt_required
    def get(self, _id_):
        song = SongModel.find_by_id(_id_)
        if song:
            return song.json()
        return {'msg': 'Song Not Exists'}

    @jwt_required
    def delete(self,_id_):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'msg': "Admin Previllage Required."}, 401
        song = SongModel.find_by_id(_id_)
        if song:
            song.delete_from_db()
            return {'msg': 'Song deleted successfully!!'}, 200
            #return {'msg': 'Unsuccessful Operation!'}, 400
        return {'msg': "Song Not Exists!"}, 400

    def put(self,_id_):
        request_data = Song.parser.parse_args()
        updated_song = SongModel.find_by_id(_id_)
        song_to_update = SongModel(**request_data)
        # !!! Check song if exists or not
        if updated_song:
            # !!! update the existing song
            try:
                song_to_update.update_song(_id_, request_data)
            except:
                return {'msg': "Error Ocurrs During Operations!"}, 500 
        else:
            # !!! Create new song if not exists
            try:
                song_to_update.save_to_db()
            except:
                return {'msg': "Error Ocurrs During Operations!"}, 500 
        return updated_song.json()


class SongList(Resource):
    
    @jwt_optional
    def get(self):
        user_id = get_jwt_identity()   # !!! get user_id from JWT Token
        songs = [song.json() for song in SongModel.query.all()]
        if user_id: # !!! If user is logged in, show him full data
            # same: {'songs': list(map(lambda x: x.json, SongModel.query.all()))}
            return{'songs': songs}, 200  # same: SELECT * FROM songs
        # !!! If user is not logged in, just give them a few
        return {
            'songs' : [song["title"] for song in songs],
            'msg' : "Log in for more information!!"
        }, 200

    @fresh_jwt_required   # !!! Token must be fresh in order to post a song
    def post(self):
        request_data = Song.parser.parse_args()
        new_song = SongModel(**request_data)
        try:
            new_song.save_to_db()
        except:
            return {'msg': 'Error occurs during the operation!'}, 500
        return new_song.json()
