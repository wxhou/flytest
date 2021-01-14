#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os
import sys

# 项目目录
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

WIN = sys.platform.startswith('win')

# 数据库前缀
prefix = 'sqlite:///' if WIN else 'sqlite:////'


class BaseConfig(object):
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev key')
    # debugtoolbar关闭重定向拦截
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    # 数据库
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    # 邮箱
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = 994
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = ('test platform', MAIL_USERNAME)
    # 上传目录
    WFTEST_UPLOAD_PATH = 'uploads'
    # flask_avatars保存目录
    AVATARS_SAVE_PATH = os.path.join(WFTEST_UPLOAD_PATH,'avatars')


class DevelopmentConfig(BaseConfig):
    """开发环境"""
    SQLALCHEMY_DATABASE_URI = prefix + os.path.join(BASE_DIR, 'data-dev.db')


class ProductionConfig(BaseConfig):
    """"线上环境"""
    SQLALCHEMY_DATABASE_URI = prefix + os.path.join(BASE_DIR, 'data.db')


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
if __name__ == "__main__":
    print(BASE_DIR)
