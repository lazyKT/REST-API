from werkzeug.security import safe_str_cmp
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token, 
    jwt_refresh_token_required,
    get_jwt_identity,
    jwt_required,
    get_raw_jwt,
    get_jwt_claims
)
from flask_restful import Resource, reqparse
from models.users import UserModel, Hash_Password
from __wrappers__ import is_admin
import os

class UserRegister(Resource):
    
    # !!! request parsing arguments
    parser = reqparse.RequestParser()
    parser.add_argument('username', type=str, required=True, help="This field cannot be empty!")
    parser.add_argument('email', type=str, required=False, help="This field cannot be empty!")
    parser.add_argument('password', type=str, required=True, help="This field cannot be empty!")
    parser.add_argument('role', type=str, required=False)
    parser.add_argument('profile_pic', type=str, required=False)


    def post(self):
        # !!! Fetch data from request parser aka reqparse
        data =  UserRegister.parser.parse_args()
    
        if UserModel.find_by_email(data['email']):
            return {'msg' : "This email already has registered account."}, 400
        
        if UserModel.find_by_username(data['username']):
            return {'msg' : "Username '{}' already exists!".format(data['username'])}, 400

        # !!! Add user to database
        user_role = "user" if data['role'] == '' else "admin"
        # salt = os.urandom(32)
        pwd = Hash_Password(data['password'])
        password = pwd.hash_pwd()

        new_user = UserModel(data['username'], data['email'], password, user_role, data['profile_pic'])
        try:
            new_user.register()
        except:
            return {'msg': 'Error Occurs During the Operation!'}, 500
        return new_user.json(), 201


    @jwt_required
    @is_admin
    def get(self):
        return {'users' : [user.json() for user in UserModel.query.all()]}


class User(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('username', type=str, required=True, help="This field cannot be empty!")
    parser.add_argument('email', type=str, required=False, help="This field cannot be empty!")
    #.add_argument('password', type=str)

    @jwt_required
    def get(self, user_id):
        user = UserModel.find_by_id(user_id)
        current_user = get_jwt_identity()
        if not user_id == current_user:
            return {'msg': "Unauthorized Content!"}, 401
        if user:
            return user.json(), 200 
        return {'msg': "User Not Found!"}, 404

    @jwt_required
    @is_admin
    def delete(self, user_id):
        user = UserModel.find_by_id(user_id)
        if user:
            UserModel.delete(user)
            return {'msg': "User deleted successfully!!!"}, 200
        return {'msg': "User Not Found!"}, 404


    @jwt_required
    def put(self, user_id):
        user = UserModel.find_by_id(user_id)
        current_user = get_jwt_identity()

        if get_jwt_claims()['is_admin']: # Is admin. the editing is allowed.
            UserModel.update(user_id, self.parser.parse_args())
            return {'msg': "Successfully Updated!!!"}, 200

        if  user_id != current_user: # Strictly prevent users to access others' data
                return {'msg': "Not Accessible Content!!!"}, 401

        if user: # Users are only allowed to edit their ownself data
            UserModel.update(user_id, self.parser.parse_args())
            return {'msg': "Successfully Updated!!!"}, 200

        return {'msg': "User Not Found!"}, 404


class UserLogin(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('username', type=str, required=True, help="Username must not be blank!")
    parser.add_argument('password', type=str, required=True, help="Password must not be blank!") 

    def post(self):
        data = self.parser.parse_args()
        user = UserModel.find_by_username(data["username"])

        # !!! below is the same with the authentication used in JWT(app,authentication,identity)
        if user and Hash_Password.check_pwd(data["password"], user.password):
            # !!! identity= is the same with the identity used in JWT(app,authentication,identity)
            access_token = create_access_token(identity=user.id, fresh=True, expires_delta=False)  # !!! Create Token for authentication
            refresh_token = create_refresh_token(user.id) # !!! Refreshing token to extend authenticated period
            return {
                'id': user.id,
                'access_token': access_token,
                'refresh_token': refresh_token,
                'role': user.role,
                'username': user.username,
                'uuid': user.user_id,
                'email': user.email
            }, 200

        return {'msg': "Invalid Credentials!!!"}, 401



class UserLogout(Resource):

    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti'] # !!! jti = JWT ID
        UserModel.BLACKLIST.add(jti) # Add the user_id to be revoked for logout
        return {'msg': "Successfully Logged Out!!"}, 200


class TokenRefresh(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('password', required=True, help="Please enter your password to countinue")

    @jwt_refresh_token_required
    def post(self):
        current_user_id = get_jwt_identity()
        current_user = UserModel.find_by_id(current_user_id)
        if not Hash_Password.check_pwd(self.parser.parse_args()["password"], current_user.password):
            return {'msg': "Wrong Credentials!"}, 401
        new_token = create_access_token(identity=current_user_id, fresh=False, expires_delta=False)
        return {'access_token': new_token}, 200


class ChangePassword(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('new_pwd', required=True, help="Data must not be empty!!!")

    @jwt_required
    def put(self, _id):
        user = UserModel.find_by_id(_id)
        current_id = get_jwt_identity()

        pwd = Hash_Password(self.parser.parse_args()['new_pwd'])
        password = pwd.hash_pwd()

        if user.id != current_id:
            return {'msg': "Invalid Requests"}, 401
        
        if user:
            UserModel.changePwd(_id, password)
            return {'msg': "Password has been changed!"}, 200
        else:
            return {'msg': "User Not Found!!"}, 404


class UserList(Resource):

    @jwt_required
    @is_admin
    def get(self):
        return {'users': [user.json() for user in UserModel.query.all()]}, 200