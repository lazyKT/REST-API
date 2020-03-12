from db import db


# !!! This is a helper class to simplify the db operations
"""
 Rule for the User Model: 
 username and email must be unique.
 One user per One email.
 Email should be valid.
"""

class UserModel(db.Model):

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
            'password': self.password,
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

    # !!! Uesr Register and Add The User's data to Database
    def register(self):
        print("User Registering.....")
        db.session.add(self)
        db.session.commit()

    # !!! Users will key in their username or email, together with the password
    # !!! Check the user type whether the username or email, then autheticate with password
    def login(self, data):
        if UserModel.find_by_email(data['username_email']):
            return self.query.filter_by(email=data['username_email']).filter_by(password=data['password']).first()
        elif UserModel.find_by_username(data['username_email']):
            return self.query.filter_by(username=data['username_email']).filter_by(password=data['password']).first()