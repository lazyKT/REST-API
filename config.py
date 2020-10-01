import os


DEBUG = False
CELERY_TASKMETA_URL = 'postgres://kt:Kyawthit18$@localhost:5432/kt'
SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI", "sqlite:///data.db")
