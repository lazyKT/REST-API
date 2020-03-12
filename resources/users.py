import sqlite3
from flask_restful import Resource, reqparse
from flask import request
from models.users import UserModel

print("Running UserModel.py....")

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
        # !!! Check email to prevent multiple accounts by single email
        if UserModel.find_by_email(data['email']):
            return {'msg' : "This email already has registered account."}, 400
        # !!! Check duplicate username in database
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


        # !!! 201 is Http request, means "created"
        return {'msg' : "User created successfully"}, 201

    def get_all_users(self):
        pass