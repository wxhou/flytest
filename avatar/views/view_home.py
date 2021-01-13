#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from flask import Blueprint,flash,redirect,url_for
from flask import request, render_template
from flask_login import current_user,login_user,logout_user
from avatar.models import User

home_bp = Blueprint('', __name__)


@home_bp.route('/')
def index():
    return "hello flask"
    # return render_template('home/index.html')

@home_bp.route('/login',methods=["GET","POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('.index'))

    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get("password")
        remember = request.form.get("remember")
        if username and password:
            user =  User.query.filter_by(email=username).first()
            if user and user.verify_password(password):
                login_user(user,remember=remember)
                flash("登录成功！",'info')
                return redirect(url_for('.index'))
        flash('账户不存在','danger')
        return redirect(request.referrer) 

    return render_template('home/login.html')

@home_bp.route('/logout',methods=["GET"])
def logout():
    logout_user()
    flash("退出登录成功",'info')
    return redirect(url_for('.login'))