from flask_restful import Api
from flask import Flask
from flask_jwt_extended import JWTManager

from models.users import UserModel
from resources.users import UserRegister, User, UserLogin
from resources.songs import Song, SongList
from resources.genres import Genre, GenreList
from db import db


app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'  # !!! Link to database location
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
app.config['PROPAGATE_EXCEPTIONS'] = True  # !!! Allow JWT to raise errors to Flask
app.config['JWT_SECRET_KEY'] = "meow"

# !!! Before the first request, as in very first start of the app, Create the REQUIRED DATABASE TABLES
@app.before_first_request
def create_database_tables():
    db.create_all()

jwt = JWTManager(app)

# !!! claims are added to JWT Token for extra purposes
@jwt.user_claims_loader
def add_claims_to_jwt(identity):  # !!! identity comes from access_token
    user = UserModel.find_by_id(identity)
    if user.role == "admin":
        return {'is_admin': True}
    return {'is_admin': False}

api.add_resource(Song, '/songs/<int:_id_>')
api.add_resource(SongList, '/songs')
api.add_resource(UserRegister, '/register')
api.add_resource(Genre, '/genre/<string:name>')
api.add_resource(GenreList, '/genres')
api.add_resource(User, '/user/<int:user_id>')
api.add_resource(UserLogin, '/login')

# Main Program Here __main__
if __name__ == '__main__':
    db.init_app(app)
    app.run(port=8000, debug=True)