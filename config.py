import os
from production import CELERY_TASKMETA_URL, HOST_EMAIL, FORWARD_EMAIL

DEBUG = False
SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI", "sqlite:///data.db")
HOST_EMAIL = HOST_EMAIL
FORWARD_EMAIL = FORWARD_EMAIL
CELERY_TASKMETA_URL = CELERY_TASKMETA_URL
SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI", "sqlite:///data.db")
