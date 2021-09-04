#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from app import create_app, celeryconfig
from dotenv import load_dotenv


def init_env():
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)


def make_celery(app_name):
    celery = Celery(app_name,
                    broker=celeryconfig.broker_url,
                    backend=celeryconfig.result_backend)
    celery.config_from_object(celeryconfig)
    return celery


init_env()
my_celery = make_celery(__name__)
app = create_app(celery=my_celery)



