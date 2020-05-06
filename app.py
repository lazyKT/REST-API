from flask_restful import Api
from flask import Flask, jsonify, render_template
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from models.users import UserModel
from resources.users import UserRegister, User, UserLogin, TokenRefresh, UserLogout, UserList
from resources.songs import Song, SongList
from resources.genres import Genre, GenreList
from db import db

import models.genre as genre


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'  # !!! Link to database location
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
app.config['PROPAGATE_EXCEPTIONS'] = True  # !!! Allow JWT to raise errors to Flask
app.config['JWT_SECRET_KEY'] = "meow"
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh'] # !!! BlackList checks on both access and refresh token
api = Api(app)
CORS(app)

# !!! Before the first request, as in very first start of the app, Create the REQUIRED DATABASE TABLES
@app.before_first_request
def create_database_tables():
    db.create_all()
    status_code = genre.import_data_from_json()
    log_txt = 'Data Initialization Finished! '
    result_txt = 'Data Created! -' if status_code == 0 else 'Data Already Existed!'
    app.logger.info(log_txt+result_txt+ " Status Code - " + str(status_code))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

jwt = JWTManager(app)

# !!! claims are added to JWT Token for extra purposes
@jwt.user_claims_loader
def add_claims_to_jwt(identity):  # !!! identity comes from access_token
    user = UserModel.find_by_id(identity)
    
    if user and user.role == "admin":
        return {'is_admin': True}
    
    return {'is_admin': False}


# !!! User inside the black list cannot access specific pages
@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    return decrypted_token['jti'] in UserModel.BLACKLIST


"""Error Handling Upon Token Operations"""
@jwt.expired_token_loader   # !!! Feed Back to users upon expired token
def expired_token_callback():
    return jsonify({
        'msg': "The Token had expired!",
        'error': "token_expired"
    }), 401


@jwt.invalid_token_loader  # !!! Feed Back to users upon invalid token
def invalid_token_callback(error):
    return jsonify({
        'msg': str(error)
        }), 401


@jwt.unauthorized_loader  # !!! Request without JWT Tokens
def missing_token_callback(error):
    return jsonify({
        'msg': "Missing Valid Token!!",
        'error': "missing_token"
    }), 401

@jwt.needs_fresh_token_loader  # !!! Require JWT Tokens
def token_not_fresh_callback():
    return jsonify({
        'msg': "Token needs to be refreshed",
        'error': "fresh_token_required"
    }), 401

@jwt.revoked_token_loader  # !!! Token Revoking/ Logout
def revoked_token():
    return jsonify({
        'msg': "Token has been revoked",
        'error': "revoked_token"
    }), 401

api.add_resource(Song, '/songs/<int:_id_>')
api.add_resource(SongList, '/songs')
api.add_resource(Genre, '/genre/<int:_id>')
api.add_resource(GenreList, '/genres')
api.add_resource(UserRegister, '/register')
api.add_resource(User, '/user/<int:user_id>')
api.add_resource(UserLogin, '/login')
api.add_resource(TokenRefresh, '/refresh')
api.add_resource(UserLogout, '/logout')
api.add_resource(UserList, '/users')

# Main Program Here __main__
if __name__ == '__main__':
    db.init_app(app)
    app.run(port=8000, debug=True)