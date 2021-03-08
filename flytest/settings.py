#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os
import sys
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

win = sys.platform.startswith('win')


class BaseConfig(object):
    SECRET_KEY = os.getenv('SECRET_KEY', "ahJ#5UoEg9x1T&@n")
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
    PER_PAGE_SIZE = 10
    # flask_avatars
    MEDIA_PATH = os.path.join(basedir, 'media')
    AVATARS_SAVE_PATH = os.path.join(MEDIA_PATH, 'avatar')
    LOGGER_FILE = os.path.join(basedir, 'logs', 'server.log')


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    DB_SERVER = '127.0.0.1'
    # debugtool
    DEBUG_TB_PROFILER_ENABLED = False
    DEBUG_TB_TEMPLATE_EDITOR_ENABLED = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    # db url
    SQLALCHEMY_DATABASE_URI = "mysql://root:123456@{}:3306/flytest".format(DB_SERVER)
    # celery
    CELERY_BROKER_URL = 'redis://{}:6379/1'.format(DB_SERVER)
    CELERY_RESULT_BACKEND = 'redis://{}:6379/2'.format(DB_SERVER)
    # cache
    CACHE_CONFIG = {
        'CACHE_TYPE': "redis",  # Flask-Caching related configs
        'CACHE_REDIS_HOST': DB_SERVER,
        'CACHE_REDIS_PORT': 6379,
        "CACHE_DEFAULT_TIMEOUT": 600
    }

    # crontabs
    SCHEDULER_JOBSTORES = {
        'default': SQLAlchemyJobStore(url=SQLALCHEMY_DATABASE_URI)
    }

    SCHEDULER_EXECUTORS = {
        'default': {'type': 'threadpool', 'max_workers': 20}
    }

    SCHEDULER_JOB_DEFAULTS = {
        'coalesce': False,
        'max_instances': 3
    }

    SCHEDULER_API_ENABLED = True


class ProductionConfig(BaseConfig):
    DB_SERVER = '127.0.0.1'
    REDIS_SERVER = '127.0.0.1'
    # db url
    SQLALCHEMY_DATABASE_URI = "mysql://root:123456@{}:3306/flytest".format(DB_SERVER)
    # celery
    CELERY_BROKER_URL = 'redis://{}:6379/1'.format(REDIS_SERVER)
    CELERY_RESULT_BACKEND = 'redis://{}:6379/2'.format(REDIS_SERVER)
    # cache
    CACHE_CONFIG = {
        'CACHE_TYPE': "redis",  # Flask-Caching related configs
        'CACHE_REDIS_HOST': REDIS_SERVER,
        'CACHE_REDIS_PORT': 6379,
        "CACHE_DEFAULT_TIMEOUT": 600
    }

    # crontabs
    SCHEDULER_JOBSTORES = {
        'default': SQLAlchemyJobStore(url=SQLALCHEMY_DATABASE_URI)
    }

    SCHEDULER_EXECUTORS = {
        'default': {'type': 'threadpool', 'max_workers': 20}
    }

    SCHEDULER_JOB_DEFAULTS = {
        'coalesce': False,
        'max_instances': 3
    }

    SCHEDULER_API_ENABLED = True


class TestingConfig(DevelopmentConfig):
    TESTING = True


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing':TestingConfig
}

if __name__ == '__main__':
    print(basedir)
