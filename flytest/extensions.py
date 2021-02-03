#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import flask
from celery import Celery
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_avatars import Avatars
from flask_moment import Moment
from flytest.settings import BaseConfig


class FlaskCelery(Celery):
    """flask celery 后台任务"""

    def __init__(self, *args, **kwargs):

        super(FlaskCelery, self).__init__(*args, **kwargs)
        self.patch_task()

        if 'app' in kwargs:
            self.init_app(kwargs['app'])

    def patch_task(self):
        TaskBase = self.Task
        _celery = self

        class ContextTask(TaskBase):
            abstract = True

            def __call__(self, *args, **kwargs):
                if flask.has_app_context():
                    return TaskBase.__call__(self, *args, **kwargs)
                else:
                    with _celery.app.app_context():
                        return TaskBase.__call__(self, *args, **kwargs)

        self.Task = ContextTask

    def init_app(self, app):
        self.app = app
        self.conf.update(app.config)


celery = FlaskCelery(broker=BaseConfig.CELERY_BROKER_URL,
                     backend=BaseConfig.CELERY_RESULT_BACKEND)
db = SQLAlchemy()
cache = Cache()
moment = Moment()
avatars = Avatars()
migrate = Migrate(db=db, render_as_batch=True)
login_manager = LoginManager()
toolbar = DebugToolbarExtension()


@login_manager.user_loader
def load_user(user_id):
    from flytest.models import User
    user = User.query.get(int(user_id))
    return user


login_manager.login_view = '.login'
login_manager.login_message_category = 'warning'
login_manager.login_message = "请先登录"
