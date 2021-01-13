#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    from avatar.models import User
    user = User.query.get(user_id)
    return user

login_manager.login_view ='home.login'
login_manager.login_message_category = 'warning'
