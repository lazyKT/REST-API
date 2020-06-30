from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from models.genre import GenreModel
from schemas.genre import GenreSchema
from __wrappers__ import is_admin

genre_schema = GenreSchema()

"""
: Genre resources are currently left out from API, may be used in the future.
"""

# class Genre(Resource):

#     @classmethod
#     @jwt_required
#     def get(cls, _id):
#         genre = GenreModel.find_by_id(_id)
#         if genre:
#             return genre.json(), 200
#         return {'msg': 'Genre Not Found!!'}

#     @classmethod
#     @jwt_required
#     @is_admin
#     def delete(cls, _id):
#         genre_to_delete = GenreModel.find_by_id(_id)
#         if genre_to_delete:
#             GenreModel.delete_genre(genre_to_delete)
#             name = genre_to_delete.name
#             return {'msg': "The Genre, '{}' has been deleted!".format(name)}, 200
#         return {'msg': "Genre Exists!!"}, 400


# class GenreList(Resource):

#     @classmethod
#     @jwt_required
#     def get(cls):
#         genre_list = [genre.json() for genre in GenreModel.query.all()]
#         return genre_list, 200

#     @classmethod
#     @jwt_required   
#     @is_admin 
#     def post(cls):
#         try:
#             data = genre_schema.load(request.get_json())
#             if GenreModel.find_by_name(data['name']):
#                 return {'msg': "Genre Already Exists!"}, 400
#             new_genre = GenreModel(**data)
#             new_genre.add_genre()
#             return new_genre.json(), 201
#         except ValidationError as err:
#             return err.messages, 400
#         except:
#             return {'msg': "Error Performing Request!"}, 500
            

