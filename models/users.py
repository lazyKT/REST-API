from datetime import datetime
from db import db
import hashlib
import os
import uuid

# !!! This is a helper class to simplify the db operations
"""
 Rule for the User Model: 
 username and email must be unique.
 One user per One email.
 Email should be valid.
"""


class UserModel(db.Model):
    BLACKLIST = set()  # For revoking the Jwt Token and Log out the user

    # !!! Defining database table for user model  #SQLAlchemy
    __tablename__ = "users"
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.String)
    email = db.Column(db.String)
    username = db.Column(db.String)
    password = db.Column(db.String)
    role = db.Column(db.String)
    createdOn = db.Column(db.String)
    updatedOn = db.Column(db.String)

    def __init__(self, username, email, password, role):
        current_time = datetime.now()
        pwd = Hash_Password(password)
        hashed_pwd = pwd.hash_pwd()

        self.username = username
        self.email = email
        self.password = hashed_pwd
        self.user_id = str(uuid.uuid1())
        self.role = role
        self.createdOn = datetime.strftime(current_time, '%m/%d/%y %H:%M:%S')
        self.updatedOn = datetime.strftime(current_time, '%m/%d/%y %H:%M:%S')

    # ??? What is a @classmethod? Class Method is used to modified the class
    # !!! cls is class method instance instead of self or classname
    @classmethod
    def find_by_username(cls, username):
        # same: "SELECT * FROM users WHERE username=username"
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()  # same: SELECT * FROM users WHERE email=email

    # !!! Find user by id inside database
    @classmethod
    def find_by_id(cls, _id):
        # same: "SELECT * FROM users WHERE id=_id"
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def update(cls, _id, update_user):
        user = cls.find_by_id(_id)
        user.username = update_user['username']
        user.email = update_user['email']
        user.updatedOn = datetime.strftime(datetime.now(), '%m/%d/%y %H:%M:%S')
        db.session.commit()

    @classmethod
    def change_password(cls, _id):
        pass

    # !!! User Register and Add The User's data to Database
    def register(self):
        print(self.createdOn)
        print(type(self))
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def changePwd(cls, _id, newPwd):
        user = cls.find_by_id(_id)
        user.password = newPwd
        db.session.commit()


class Hash_Password:

    def __init__(self, pwd):
        self.salt = os.urandom(32)
        self.pwd = pwd

    def hash_pwd(self):
        key = hashlib.pbkdf2_hmac('sha256', self.pwd.encode('utf-8'), self.salt, 1000)
        store_pwd = self.salt + key

        return store_pwd

    @classmethod
    def check_pwd(cls, pwd, store_pwd):
        salt_from_storage = store_pwd[:32]
        key_from_storage = store_pwd[32:]
        key = hashlib.pbkdf2_hmac('sha256', pwd.encode('utf-8'), salt_from_storage, 1000)

        return True if key == key_from_storage else False
