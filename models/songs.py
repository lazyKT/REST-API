from db import db
from models.users import UserModel
from models.genre import GenreModel


# !!! This is a helper class to make the db operations simple and easy
class SongModel(db.Model):
    # !!! Define database table for songs model #SQLAlchemy
    __tablename__ = "songs"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    posted_by = db.Column(db.String(80))
    url = db.Column(db.String(80))

    genre_id = db.Column(db.Integer, db.ForeignKey('genres.id'))  # Genre ID as an Foreign Key For Songs
    genre = db.relationship('GenreModel')  # !!! Join two tables, genres and songs

    def __init__(self, title, posted_by,genre_id, url=""):
        self.title = title
        self.posted_by = posted_by
        self.url = url
        self.genre_id = genre_id

    # !!! This method is to convert the json into python dicts
    def json(self):
        return {
            'id': self.id,
            'title': self.title,
            'posted_by': UserModel.find_by_id(self.posted_by).username,
            'genre': GenreModel.find_by_id(self.genre_id).name
        }

    @classmethod
    def find_by_id(cls, _id_):
        return cls.query.filter_by(id=_id_).first()  # same: SELECT * FROM songs WHERE id = _id_ LIMIT 1

    # !!! the insert and update method is just to 
    # !!! insert (or) update the data into Song Model,
    # !!! so we don't need class method here
    def save_to_db(self):
        db.session.add(self)  # !!! Update or Insert into Database
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)  # same: DELETE FROM songs WHERE id = self.id
        db.session.commit()

    def update_song(self, _id_, updated_song):
        self.title = updated_song["title"]
        db.session.commit()
