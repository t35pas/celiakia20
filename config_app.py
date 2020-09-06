import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = '677a6637137a00c8c3aed7246b14d0e1d4eda1bfa4270a2f390580ddc3c3879d'
    SQLALCHEMY_DATABASE_URI = os.environ['heroku pg:psql postgresql-reticulated-37565 --app celiakia20']


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True