#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask_apscheduler import APScheduler
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_avatars import Avatars
from flask_moment import Moment
from flask_caching import Cache
from flask_assets import Environment

naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

assets = Environment()
db = SQLAlchemy(metadata=MetaData(naming_convention=naming_convention))
cache = Cache()
moment = Moment()
avatars = Avatars()
migrate = Migrate(db=db, render_as_batch=True)
login_manager = LoginManager()
toolbar = DebugToolbarExtension()
scheduler = APScheduler()

@login_manager.user_loader
def load_user(user_id):
    from flytest.models import User
    user = User.query.get(int(user_id))
    return user


def raw_sql(_sql):
    result = db.engine.execute(_sql)
    return result


login_manager.login_view = '.login'
login_manager.login_message_category = 'warning'
login_manager.login_message = "请先登录"
