from db import db
from models.users import UserModel


# !!! This is a helper class to make the db operations simple and easy
class SongModel(db.Model):
    # !!! Define database table for songs model #SQLAlchemy
    __tablename__ = "songs"
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(80)) # Celery task id
    title = db.Column(db.String(80))  # given by user
    posted_by = db.Column(db.String(80)) # user id
    url = db.Column(db.String(80)) # url related to song: example: https://www.youtube.com/watch?v=hxwjT90i8Ys


    def __init__(self, task_id, title, posted_by,genre_id, url):
        self.task_id = task_id
        self.title = title
        self.posted_by = posted_by
        self.url = url
        self.genre_id = genre_id

    """ : Callable Instance of SongModel Class """
    def __call__(self):
        return {
            'id': self.id,
            'task_id': self.task_id,
            'title': self.title,
            'posted_by': UserModel.find_by_id(self.posted_by).id,
            'url': self.url,
        }
        
    @classmethod
    def find_by_id(cls, _id_):
        return cls.query.filter_by(id=_id_).first()  # same: SELECT * FROM songs WHERE id = _id_ LIMIT 1

    # !!! : Get a song by url. 
    # : first() means that the query will return only the first result no matter how many results availbel
    @classmethod
    def find_by_url(cls, url):
        return cls.query.filter_by(url = url).first()

    """
    : This function search for the songs which is related to the user_id.
    """
    @classmethod
    def find_by_user(cls, _id_):
        # The 'posted_by' column is String type, so I need to convert _id_ to String
        return cls.query.filter_by(posted_by=str(_id_)).order_by(cls.id.desc())

    # This function prevents processing of the duplicate songs from the same user.
    @classmethod
    def check_duplication(cls, user_id, url):
        return cls.query.filter_by(posted_by=str(user_id), url=url).first()

    # This function checks if the song with the same url exists in db
    @classmethod
    def find_by_song(cls, url):
        return cls.query.filter_by(url=url).first()


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
