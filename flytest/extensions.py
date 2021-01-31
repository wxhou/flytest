#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_avatars import Avatars
from flask_moment import Moment

db = SQLAlchemy()
moment = Moment()
avatars = Avatars()
migrate = Migrate(db=db)
login_manager = LoginManager()
toolbar = DebugToolbarExtension()


@login_manager.user_loader
def load_user(user_id):
    from flytest.models import User
    user = User.query.get(int(user_id))
    return user


login_manager.login_view = 'home.login'
login_manager.login_message_category = 'warning'
login_manager.login_message = "请先登录"
