#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os
import sys

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

WIN = sys.platform.startswith('win')

# 数据库前缀
PREFIX = 'sqlite:///' if WIN else 'sqlite:////'


class BaseConfig(object):

    # key
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev key')
    # celery
    CELERY_BROKER_URL = 'redis://127.0.0.1:6379',
    CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379'
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

class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = PREFIX + os.path.join(BASE_DIR, 'data-dev.db')


class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = PREFIX + os.path.join(BASE_DIR, 'data.db')


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}

if __name__ == '__main__':
    print(BASE_DIR)
