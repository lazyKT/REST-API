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

song_schema = SongSchema


class Song(Resource):

    @classmethod
    @jwt_required
    def get(cls, _id_):
        song = SongModel.find_by_id(_id_)
        if song:
            return song_schema.dump(song), 200
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
        if not SongModel.find_by_id(_id_):
            return {"msg": "Invalid Song. Doesn't exist!!"}, 400

        song = request.get_json()
        update_song = SongModel(**song)
        try:
            update_song.update_song(_id_, song)
        except ValidationError as err:
            return {'msg': err.messages}, 400
        return song_schema.dump(SongModel.find_by_id(_id_)), 200


class SongList(Resource):

    @classmethod
    # @jwt_optional
    def get(cls):
        user_id = get_jwt_identity()  # !!! get user_id from JWT Token
        songs = [song.json() for song in SongModel.query.all()]
        return songs

    @classmethod
    @fresh_jwt_required  # !!! Token must be fresh in order to post a song
    def post(cls):
        data = Song.parser.parse_args()
        genre_exists = GenreModel.find_by_id(data['genre_id'])
        if genre_exists:
            new_song = SongModel(**data)
            try:
                new_song.save_to_db()
                return new_song.json(), 201
            except:
                return {'msg': 'Error occurs during the operation!'}, 500
        return {'msg': "Genre must be existed before song is created"}, 400
