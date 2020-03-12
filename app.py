from flask_restful import Api
from flask import Flask
from flask_jwt import JWT

from security import authenticate, identity
from resources.users import UserRegister
from resources.songs import Song, SongList
from resources.genres import Genre, GenreList
from db import db


app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'  # !!! Link to database location
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
app.secret_key = 'meow'

# !!! Before the first request, as in very first start of the app, Create the REQUIRED DATABASE TABLES
@app.before_first_request
def create_database_tables():
    db.create_all()

jwt = JWT(app, authenticate, identity)   # /auth

api.add_resource(Song, '/songs/<int:_id_>')
api.add_resource(SongList, '/songs')
api.add_resource(UserRegister, '/register')
api.add_resource(Genre, '/genre/<string:name>')
api.add_resource(GenreList, '/genres')



# Main Program Here __main__
if __name__ == '__main__':
    db.init_app(app)
    app.run(port=8000, debug=True)