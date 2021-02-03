#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os
import sys

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

WIN = sys.platform.startswith('win')

PREFIX = 'sqlite:///' if WIN else 'sqlite:////'

# key
SECRET_KEY = os.getenv('SECRET_KEY', 'dev key')
# celery
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/1',
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/2'
# mysql
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_RECORD_QUERIES = True
# email
MAIL_SERVER = os.getenv('MAIL_SERVER')
MAIL_PORT = 994
MAIL_USE_SSL = True
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
MAIL_DEFAULT_SENDER = ('flytest', MAIL_USERNAME)
PER_PAGE_SIZE = 15
# flask_avatars
AVATARS_SAVE_PATH = os.path.join(BASE_DIR, 'avatar')

DEBUG_TB_INTERCEPT_REDIRECTS = False
# cache
CACHE_REDIS_URL = 'redis://:@127.0.0.1:6379/3'
CACHE_DEFAULT_TIMEOUT = 60
# db url
SQLALCHEMY_DATABASE_URI = PREFIX + os.path.join(BASE_DIR, 'data-dev.db')

CACHE_CONFIG = {
    'CACHE_TYPE': "redis",  # Flask-Caching related configs
}
