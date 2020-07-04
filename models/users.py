from datetime import datetime
from db import db
import hashlib
import os
import uuid
from lib.email_helper import send
from flask import url_for, request, render_template

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
    password = db.Column(db.LargeBinary)
    role = db.Column(db.String)
    status = db.Column(db.String)
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
        self.status = 'InActive'
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

    """
    : After the successful registeration of the account, an email linked to account activation has been sent to user's email address.
    : User can only login after the account has been activated.
    : This function simply perform the email delivery to the destinated user's email address using SENDGRID Twilio API.
    """
    @classmethod
    def send_confirmation_email(cls, token, email, username):
        print("Send Confirmation Email")
        activate_url = request.url_root[:-1] + f'/confirm/{token}'
        sender = os.environ.get('HOST_EMAIL')
        subject = os.environ.get('USER_CREATED_SUBJECT')
        print("Before Body")
        body = render_template('confirm_email.html', confirm_url = activate_url, username = username)
        send(sender, email, subject, body)
    
    """
    : This is a helper function for the users.password_forget(email) function.
    : This function actually sends the pwd-rest-link to given email address.
    """
    @classmethod
    def send_pwd_reset_link(cls, token, username, email):
        print("Sending Password Reset Link")
        link = request.url_root[:-1] + f'/reset-password/{token}'
        sender = os.environ.get('HOST_EMAIL')
        subject = os.environ.get('FORGET_PASSWORD_SUBJECT')
        body = render_template('pwd_reset_email.html', username = username, reset_link = link)
        send(sender, email, subject, body)

    """
    : This is helper function for the route, '/activate/user_id'.
    : This function does the activation of the inactive accounts by simply query the db row.
    """
    @classmethod
    def activate_account(cls, user_id):
        user = cls.find_by_id(user_id)
        user.status = 'Active'
        db.session.commit()

    """
    : This is a helper function for the deactivation of the account.
    : This function performs the Database Query and mutate the row.
    """
    @classmethod
    def deactivate_account(cls, user_id):
        user = cls.find_by_id(user_id)
        user.status = 'InActive'
        db.session.commit()


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
        sender = os.environ.get('HOST_EMAIL')
        subject = os.environ.get('PASSWORD_CHAGED_SUBJECT')
        body = render_template('pwd_changed_email.html', username = user.username)
        send(sender, user.email, subject, body)


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
        print(store_pwd)
        print(str(store_pwd).encode('utf-8'))
        salt_from_storage = store_pwd[:32]
        key_from_storage = store_pwd[32:]
        key = hashlib.pbkdf2_hmac('sha256', pwd.encode('utf-8'), salt_from_storage, 1000)
        #print(f'{salt_from_storage} {key_from_storage} {key}')
        return True if key == key_from_storage else False
