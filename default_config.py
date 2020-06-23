import os


SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = True
SQLALCHEMY_DATABASE_URI = "sqlite:///data.db"
SQLALCHEMY_DATABASE_MODIFICATIONS = False
PROPAGATE_EXCEPTIONS = True
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
JWT_BLACKLIST_ENABLED = True
JWT_BLACKLIST_TOKEN_CHECKS = ["access", "refresh"]
UPLOADED_IMAGES_DEST = os.path.join("static", "images")
CELERY_RESULT_BACKEND="db+sqlite:///data.db"
CELERY_BROKER_URL='redis://localhost:6379/0'
