from db import db


# !!! This is a helper class to make the db operations simple and easy
class SongModel(db.Model):
    # !!! Define database table for songs model #SQLAlchemy
    __tablename__ = "songs"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    artist = db.Column(db.String(80))
    song_url = db.Column(db.String(80))

    genre_id = db.Column(db.Integer, db.ForeignKey('genres.id'))  # Genre ID as an Foreign Key For Songs
    genre = db.relationship('GenreModel')  # !!! Join two tables, genres and songs

    def __init__(self, title, artist, genre_id):
        self.title = title
        self.artist = artist
        self.genre_id = genre_id

    # !!! This method is to convert the json into python dicts
    def json(self):
        return {'id': self.id, 'title': self.title, 'artist': self.artist, 'genre_id': self.genre_id}

    @classmethod
    def find_by_id(cls, _id_):
        ##print("Searching for a song with ID : " + str(_id_))
        return cls.query.filter_by(id=_id_).first()  # same: SELECT * FROM songs WHERE id = _id_ LIMIT 1

    # !!! the insert and update method is just to 
    # !!! insert (or) update the data into Song Model,
    # !!! so we don't need classmethod here
    def save_to_db(self):
        # debug: print("Inserting new rows into songs")
        db.session.add(self)  # !!! Update or Insert into Database
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)  # same: DELETE FROM songs WHERE id = self.id
        db.session.commit()

    def update_song(self, _id_, updated_song):
        song_to_update = self.find_by_id(_id_)
        song_to_update.title = updated_song["title"]
        song_to_update.artist = updated_song["artist"]
        # song_to_update.genre_id = updated_song["genre_id"]
        db.session.commit()
