#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_avatars import Avatars
from flask_moment import Moment
from flask_caching import Cache
from flask_assets import Environment


assets = Environment()
db = SQLAlchemy()
cache = Cache()
moment = Moment()
avatars = Avatars()
migrate = Migrate(db=db, render_as_batch=True)
login_manager = LoginManager()
scheduler = APScheduler()


@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    user = User.query.get(int(user_id))
    return user


def raw_sql(_sql):
    result = db.engine.execute(_sql)
    return result


login_manager.login_view = '/login'
login_manager.login_message_category = 'warning'
login_manager.login_message = "请先登录"
