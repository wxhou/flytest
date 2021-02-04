#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os
import sys

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

WIN = sys.platform.startswith('win')
# prefix
PREFIX = 'sqlite:///' if WIN else 'sqlite:////'
# key
SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(13))
# celery
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/1',
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/2'
# mysql
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_RECORD_QUERIES = True
# email
MAIL_SERVER = os.getenv('MAIL_SERVER')
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
MAIL_DEFAULT_SENDER = ('flytest', MAIL_USERNAME)
PER_PAGE_SIZE = 15
# flask_avatars
AVATARS_SAVE_PATH = os.path.join(BASE_DIR, 'avatar')
# debugtool
DEBUG_TB_INTERCEPT_REDIRECTS = False
# db url
SQLALCHEMY_DATABASE_URI = PREFIX + os.path.join(BASE_DIR, 'data-dev.db')
# cache
CACHE_CONFIG = {
    'CACHE_TYPE': "redis",  # Flask-Caching related configs
    'CACHE_REDIS_HOST': '127.0.0.1',
    'CACHE_REDIS_PORT': 6379,
    "CACHE_DEFAULT_TIMEOUT": 600
}
