from werkzeug.security import safe_str_cmp
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_restful import Resource, reqparse
from models.users import UserModel

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

    def get(self):
        return {'users' : [user.json() for user in UserModel.query.all()]}


class User(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('username', type=str, required=True, help="This field cannot be empty!")
    parser.add_argument('email', type=str, required=False, help="This field cannot be empty!")
    parser.add_argument('password', type=str)

    @classmethod
    def get(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if user:
            return user.json()
        return {'msg': "User Not Found!"}, 404

    @classmethod
    def delete(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if user:
            UserModel.delete(user)
            return {'msg': "User deleted successfully!!!"}, 200
        return {'msg': "User Not Found!"}, 404

    def put(self, user_id):
        user = UserModel.find_by_id(user_id)
        if user:
            print("Before Update_______")
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