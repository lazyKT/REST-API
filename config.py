import os


DEBUG = False
<<<<<<< HEAD
SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI", "sqlite:///data.db")
HOST_EMAIL = "kyaw.thitlwin.me@gmail.com"
FORWARD_EMAIL = "kyaw.thitlwin.dev@gmail.com"
=======
CELERY_TASKMETA_URL = 'postgres://kt:Kyawthit18$@localhost:5432/kt'
SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI", "sqlite:///data.db")
>>>>>>> 3a3c7014afcedfa63eadfa26a80a6bc4697c67fc
