from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
import json
from models.songs import SongModel


class Song(Resource):

    # initiate reqparse which is similar to Patch
    # request parsing, validate the payload
    parser = reqparse.RequestParser()
    parser.add_argument('title', required=True, help="This field cannot be empty!")
    parser.add_argument('artist',required=True,help="This field cannot be empty!")
    parser.add_argument('genre_id',required=True,help="Song must have genre!")

    @jwt_required()
    def get(self, _id_):
        song = SongModel.find_by_id(_id_)
        if song:
            return song.json()
        return {'msg': 'Song Not Exists'}

    def delete(self,_id_):
        song = SongModel.find_by_id(_id_)
        if song:
            song.delete_from_db()
            return {'msg': 'Song deleted successfully!!'}, 200
            #return {'msg': 'Unsuccessful Operation!'}, 400
        return {'msg', 'Song Not Exists!'}, 400

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
    
    #@jwt_required()
    def get(self):
        # same: {'songs': list(map(lambda x: x.json, SongModel.query.all()))}
        return{'songs': [song.json() for song in SongModel.query.all()]}  # same: SELECT * FROM songs

    def post(self):
        request_data = Song.parser.parse_args()
        new_song = SongModel(**request_data)
        try:
            new_song.save_to_db()
        except:
            return {'msg': 'Error occurs during the operation!'}, 500
        return new_song.json()
