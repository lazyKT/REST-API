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
from models.users import UserModel
from blacklist import BLACKLIST
from __wrappers__ import is_admin

class UserRegister(Resource):
    
    # !!! request parsing arguments
    parser = reqparse.RequestParser()
    parser.add_argument('username', type=str, required=True, help="This field cannot be empty!")
    parser.add_argument('email', type=str, required=False, help="This field cannot be empty!")
    parser.add_argument('password', type=str, required=True, help="This field cannot be empty!")
    parser.add_argument('role', type=str, required=False)


    def post(self):
        # !!! Fetch data from request parser aka reqparse
        data =  UserRegister.parser.parse_args()
        if UserModel.find_by_email(data['email']):
            return {'msg' : "This email already has registered account."}, 400
        if UserModel.find_by_username(data['username']):
            return {'msg' : "Username '{}' already exists!".format(data['username'])}, 400
        # !!! Add user to database
        user_role = "user" if data['role'] == '' else "admin"
        new_user = UserModel(data['username'], data['email'], data['password'], user_role)
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
    parser.add_argument('password', type=str)

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
        if user_id != current_user:
                return {'msg': "Not Accessible Content!!!"}, 401
        if user:
            #print("Before Update_______")
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
        if user and safe_str_cmp(user.password, data["password"]):
            # !!! identity= is the same with the identity used in JWT(app,authentication,identity)
            access_token = create_access_token(identity=user.id, fresh=True)  # !!! Create Token for authentication
            refresh_token = create_refresh_token(user.id) # !!! Refreshing token to extend authenticated period
            return {
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 200
        return {'msg': "Invalid Credentials!!!"}, 401


class UserLogout(Resource):

    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti'] # !!! jti = JWT ID
        BLACKLIST.add(jti)
        return {'msg': "Successfully Logged Out!!"}, 200


class TokenRefresh(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('password', required=True, help="Please enter your password to countinue")

    @jwt_refresh_token_required
    def post(self):
        current_user_id = get_jwt_identity()
        current_user = UserModel.find_by_id(current_user_id)
        if not safe_str_cmp(current_user.password, self.parser.parse_args()['password']):
            return {'msg': "Wrong Credentials!"}, 401
        new_token = create_access_token(identity=current_user_id, fresh=False)
        return {'access_token': new_token}, 200

class UserList(Resource):

    @jwt_required
    @is_admin
    def get(self):
        return {'users': [user.json() for user in UserModel.query.all()]}, 200