import os
import logging

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'your_secret_key'

    LOGGING_LEVEL = 'DEBUG'
    LOGGING_FORMAT = '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    LOGGING_LOCATION = 'app.log'
    LOGGING_MAX_BYTES = 10000000
    LOGGING_BACKUP_COUNT = 5
    