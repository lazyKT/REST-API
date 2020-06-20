import os
from marshmallow import ValidationError
from flask import request, url_for
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_refresh_token_required,
    get_jwt_identity,
    jwt_required,
    get_raw_jwt,
    get_jwt_claims
)
from flask_restful import Resource
from models.users import UserModel, Hash_Password
from schemas.user_schema import UserSchema
from __wrappers__ import is_admin

user_schema = UserSchema()


class UserRegister(Resource):

    @classmethod
    def post(cls):
        try:
            user = user_schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400

        if UserModel.find_by_username(user['username']):
            return {"msg": "User Already Exists"}, 400

        if UserModel.find_by_email(user['email']):
            return {"msg": "This email already has a registered account."}, 400

        new_user = UserModel(**request.get_json())
        try:
            new_user.register()
            print("User Registered...")
            new_user.send_confirmation_email()
        except:
            return {'msg': "Error Performing Request!!"}, 500

        return {'msg': user_schema.dump(new_user)}, 201


class User(Resource):

    @classmethod
    @jwt_required
    def get(cls, user_id):
        if get_jwt_identity() != user_id:
            return {'msg': "Unauthorized Content"}, 401
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'msg': "Invalid User!! User Not Exists!!"}, 400
        return user_schema.dump(user), 200

    @classmethod
    @jwt_required
    @is_admin
    def delete(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if user:
            UserModel.delete(user)
            return {'msg': "User deleted successfully!!!"}, 200
        return {'msg': "User Not Found!"}, 404

    @classmethod
    @jwt_required
    def put(cls, user_id):
        user = UserModel.find_by_id(user_id)
        current_user = get_jwt_identity()

        if not user:
            return {'msg': "User Not Found!!"}, 400

        try:
            if current_user == user_id or get_jwt_claims()['is_admin']:
                edit_user = user_schema.load(request.get_json())
                UserModel.update(user_id, edit_user)
                return {'msg': "Successfully Updated!!"}, 200
            return {'msg': "Unauthorized Content!!"}, 401
        except ValidationError as err:
            return err.messages, 400
        except:
            return {'msg': "Error Performing Request!!"}, 500


class UserLogin(Resource):

    @classmethod
    def post(cls):
        data = user_schema.load(request.get_json())
        user = UserModel.find_by_username(data["username"])

        # !!! below is the same with the authentication used in JWT(app,authentication,identity)
        if user and Hash_Password.check_pwd(data["password"], user.password):
            # !!! identity= is the same with the identity used in JWT(app,authentication,identity)
            access_token = create_access_token(identity=user.id, fresh=True,
                                               expires_delta=False)  # !!! Create Token for authentication
            refresh_token = create_refresh_token(user.id)  # !!! Refreshing token to extend authenticated period
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


class TokenRefresh(Resource):

    @classmethod
    @jwt_refresh_token_required
    def post(cls):
        data = user_schema.load(request.get_json())
        current_user_id = get_jwt_identity()
        current_user = UserModel.find_by_id(current_user_id)
        if not Hash_Password.check_pwd(data["password"], current_user.password):
            return {'msg': "Wrong Credentials!"}, 401
        new_token = create_access_token(identity=current_user_id, fresh=False, expires_delta=False)
        return {'access_token': new_token}, 200


class ChangePassword(Resource):

    @classmethod
    @jwt_required
    def put(cls, _id):
        data = user_schema.load(request.get_json())
        user = UserModel.find_by_id(_id)
        current_id = get_jwt_identity()

        pwd = Hash_Password(data['password'])
        password = pwd.hash_pwd()

        if user.id != current_id:
            return {'msg': "Invalid Requests"}, 401

        if user:
            UserModel.changePwd(_id, password)
            return {'msg': "Password has been changed!"}, 200
        else:
            return {'msg': "User Not Found!!"}, 404


class UserLogout(Resource):
    @classmethod
    @jwt_required
    def post(cls):
        print("Logout----------------------")
        jti = get_raw_jwt()['jti']  # !!! jti = JWT ID
        UserModel.BLACKLIST.add(jti)  # Add the user_id to be revoked for logout
        return {'msg': "Successfully Logged Out!!"}, 200


class UserList(Resource):

    @classmethod
    @jwt_required
    @is_admin
    def get(cls):
        return {'users': [user_schema.dump(user) for user in UserModel.query.all()]}, 200
