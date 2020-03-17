from db import db


# !!! This is a helper class to simplify the db operations
"""
 Rule for the User Model: 
 username and email must be unique.
 One user per One email.
 Email should be valid.
"""

class UserModel(db.Model):

    BLACKLIST = set() # For revoking the Jwt Token and Log out the user

    # !!! Defining database table for user model  #SQLAlchemy
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    email = db.Column(db.String(80))
    password = db.Column(db.String(80))
    role = db.Column(db.String(80))

    def __init__(self, username, email, password, role):
        self.username = username
        self.email = email
        self.password = password
        self.role = role
    
    def json(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role 
        }

    #??? What is a @classmethod? Class Method is used to modified the class
    #!!! cls is class method instance instead of self or classname
    @classmethod
    def find_by_username(cls,username):
        # same: "SELECT * FROM users WHERE username=username"
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_email(cls,email):
        return cls.query.filter_by(email=email).first() # same: SELECT * FROM users WHERE email=email


    # !!! Find user by id inside database
    @classmethod
    def find_by_id(cls,_id):
        # same: "SELECT * FROM users WHERE id=_id"
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def update(cls, _id, update_user):
        user = cls.find_by_id(_id)
        user.username = update_user['username']
        user.email = update_user['email']
        db.session.commit()

    @classmethod
    def change_password(cls, _id):
        pass

    # !!! Uesr Register and Add The User's data to Database
    def register(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()