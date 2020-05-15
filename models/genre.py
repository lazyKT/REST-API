from db import db
import os
import json


# !!! This is a helper class to simplify the db operations
class GenreModel(db.Model):
    # !!! Defining database table for user model  #SQLAlchemy
    __tablename__ = "genres"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    url = db.Column(db.String(80))

    songs = db.relationship('SongModel', lazy='dynamic')  # !!! Join two tables, genres and songs

    def __init__(self, name, url=""):
        self.name = name
        self.url = url

    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'songs': [song.json() for song in self.songs.all()]
        }

    # ??? What is a @classmethod? Class Method is used to modified the class
    # !!! cls is class method instance instead of self or classname
    @classmethod
    def find_by_name(cls, name):
        # same: "SELECT * FROM users WHERE name=name"
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_by_id(cls, genre_id):
        return cls.query.filter_by(id=genre_id).first()

    def add_genre(self):
        db.session.add(self)
        db.session.commit()

    def delete_genre(self):
        db.session.delete(self)
        db.session.commit()

    # def import_data_from_json(self):
    #     file_path = ''
    #     json_file = ''
    #     json_data = ''

    #     for data in json_data['name']:
    #         self.add_genre(data)


def import_data_from_json():
    json_file = open('genres.json')
    json_data = json.load(json_file)

    for data in json_data:
        genre = GenreModel.find_by_name(data['name'])
        if genre:
            return 1
        else:
            new_genre = GenreModel(data['name'])
            new_genre.add_genre()

    return 0
