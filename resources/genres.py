from flask_restful import Resource, reqparse
from models.genre import GenreModel

class Genre(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('name', required=True ,help="This field must be filled out!")
    
    def get(self, name):
        genre = GenreModel.find_by_name(name)
        return genre.json() if genre else {'msg': 'Genre Not Found!!'}, 404

    def post(self, name):
        if GenreModel.find_by_name():
            return {'msg': "Genre with name '{}' already exists!".format(name)}, 400
        try:
            new_genre = GenreModel(name)
            new_genre.add_genre()
            return new_genre.json()
        except:
            return {'msg': "Error occurs during the operation!!"}, 500

    def delete(self, name):
        if GenreModel.find_by_name(name):
            GenreModel.delete_genre(name)
            return {'msg': "The Genre, '{}' has been deleted!".format(name)}, 200
        return {'msg': "The Genre, '{}' not exists!!".format(name)}, 400

class GenreList(Resource):

    def get(self):
        genre_list = [genre.json() for genre in GenreModel.query.all()]
        return {'genres' : genre_list}
    
    def post(self):
        data = Genre.parser.parse_args()
        if GenreModel.find_by_name(data['name']):
            return {'msg': "Genre already Exists!"}
        new_genre = GenreModel(data['name'])
        new_genre.add_genre()
        return {'msg': "Genre, '{}' has been created!!".format(data['name'])}, 201
            

