#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os
import sys

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

win = sys.platform.startswith('win')

# 数据库前缀
prefix = 'sqlite:///' if win else 'sqlite:////'


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
    AVATARS_SAVE_PATH = os.path.join(basedir, 'avatar')

    DEBUG_TB_INTERCEPT_REDIRECTS = False

    CACHE_TYPE = "redis",  # Flask-Caching related configs


class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = prefix + os.path.join(basedir, 'data-dev.db')


class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = prefix + os.path.join(basedir, 'data.db')


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}

cache_config = {
    'CACHE_TYPE': "redis",  # Flask-Caching related configs
}

if __name__ == '__main__':
    print(BASE_DIR)
