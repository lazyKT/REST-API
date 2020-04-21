from flask_restful import Resource, reqparse
from models.genre import GenreModel
from flask_jwt_extended import jwt_required, get_jwt_claims
from __wrappers__ import is_admin


class Genre(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('name', required=True ,help="This field must be filled out!")
    
    @jwt_required
    def get(self, name):
        genre = GenreModel.find_by_name(name)
        if genre:
            return genre.json(), 200
        return {'msg': 'Genre Not Found!!'}

    @jwt_required
    @is_admin
    def post(self, name):
        if GenreModel.find_by_name():
            return {'msg': "Genre with name '{}' already exists!".format(name)}, 400
        try:
            new_genre = GenreModel(name)
            new_genre.add_genre()
            return new_genre.json()
        except:
            return {'msg': "Error occurs during the operation!!"}, 500

    @jwt_required
    @is_admin
    def delete(self, name):
        genre_to_delete = GenreModel.find_by_name(name)
        if genre_to_delete:
            GenreModel.delete_genre(genre_to_delete)
            return {'msg': "The Genre, '{}' has been deleted!".format(name)}, 200
        return {'msg': "The Genre, '{}' not exists!!".format(name)}, 400


class GenreList(Resource):

    @jwt_required
    def get(self):
        genre_list = [genre.json() for genre in GenreModel.query.all()]
        return genre_list, 200

    @jwt_required   
    @is_admin 
    def post(self):
        data = Genre.parser.parse_args()
        if GenreModel.find_by_name(data['name']):
            return {'msg': "Genre already Exists!"}
        new_genre = GenreModel(data['name'])
        new_genre.add_genre()
        return {'msg': "Genre, '{}' has been created!!".format(data['name'])}, 201
            

