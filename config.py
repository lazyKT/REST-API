import os


DEBUG = False
SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI", "sqlite:///data.db")
HOST_EMAIL = "kyaw.thitlwin.me@gmail.com"
FORWARD_EMAIL = "kyaw.thitlwin.dev@gmail.com"
CELERY_TASKMETA_URL = 'sqlite:///data.db'
SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI", "sqlite:///data.db")
