from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    jwt_required,
    get_jwt_claims,
    jwt_optional,
    get_jwt_identity,
    fresh_jwt_required
)
from flask import request
from marshmallow import ValidationError
from schemas.songs import SongSchema
from models.songs import SongModel
from models.genre import GenreModel
from __wrappers__ import is_admin

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
        songs = [song.json() for song in SongModel.query.all()]
        return songs

    @classmethod
    # @fresh_jwt_required  # !!! Token must be fresh in order to post a song
    def post(cls):
        try:
            song_data = song_schema.load(request.get_json())
            genre = GenreModel.find_by_id(song_data['genre_id'])
            if genre:
                new_song = SongModel(**song_data)
                new_song.save_to_db()
                return new_song.json(), 201
            return {'msg': "Invalid Genre! Not Exists!"}, 400
        except ValidationError as err:
            return err.messages, 400
        except:
            return {'msg': "Error Performing Request!"}, 500

