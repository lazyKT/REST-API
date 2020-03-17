from db import db


# !!! This is a helper class to simplify the db operations
class GenreModel(db.Model):

    # !!! Defining database table for user model  #SQLAlchemy
    __tablename__ = "genres"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))

    songs = db.relationship('SongModel', lazy='dynamic') # !!! Join tow tables, genres and songs

    def __init__(self, name):
        self.name = name
    
    def json(self):
        return {
            'name': self.name,
            'songs': [song.json() for song in self.songs.all()]  
        }

    #??? What is a @classmethod? Class Method is used to modified the class
    #!!! cls is class method instance instead of self or classname
    @classmethod
    def find_by_name(cls,name):
        # same: "SELECT * FROM users WHERE name=name"
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_by_id(cls,genre_id):
        return cls.query.filter_by(id=genre_id).first()


    def add_genre(self):
        db.session.add(self)
        db.session.commit()

    def delete_genre(self):
        db.session.delete(self)
        db.session.commit()