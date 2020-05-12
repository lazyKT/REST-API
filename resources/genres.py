from flask_restful import Resource, reqparse
from models.genre import GenreModel
from flask_jwt_extended import jwt_required, get_jwt_claims
from __wrappers__ import is_admin


class Genre(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('name', required=True, help="This field must be filled out!")
    parser.add_argument('cover_url', required=False)

    @classmethod
    @jwt_required
    def get(cls, _id):
        genre = GenreModel.find_by_id(_id)
        if genre:
            return genre.json(), 200
        return {'msg': 'Genre Not Found!!'}

    @classmethod
    @jwt_required
    @is_admin
    def delete(cls, _id):
        genre_to_delete = GenreModel.find_by_id(_id)
        if genre_to_delete:
            GenreModel.delete_genre(genre_to_delete)
            name = genre_to_delete.name
            return {'msg': "The Genre, '{}' has been deleted!".format(name)}, 200
        return {'msg': "Genre Exists!!"}, 400


class GenreList(Resource):

    @classmethod
    @jwt_required
    def get(cls):
        genre_list = [genre.json() for genre in GenreModel.query.all()]
        return genre_list, 200

    @classmethod
    @jwt_required   
    @is_admin 
    def post(cls):
        data = Genre.parser.parse_args()
        if GenreModel.find_by_name(data['name']):
            return {'msg': "Genre already Exists!"}
        new_genre = GenreModel(data['name'], data['cover_url'])
        new_genre.add_genre()
        return {
            'id': new_genre.id,
            'name': new_genre.name,
            'cover_url': new_genre.cover_url
        }, 201
            

