#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from flask import Blueprint, flash, redirect, url_for, request, current_app, render_template, send_from_directory
from flask_login import current_user, login_user, logout_user
from avatar.models import User

home_bp = Blueprint('home', __name__)


@home_bp.route('/')
def index():
    return render_template('home/index.html', page_name='homepage')


@home_bp.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('.index'))

    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get("password")
        remember = request.form.get("remember")
        if username and password:
            user = User.query.filter_by(email=username).first()
            if user and user.verify_password(password):
                login_user(user, remember=remember)
                flash("登录成功！", 'info')
                return redirect(url_for('.index'))
        flash('账户不存在', 'danger')
        return redirect(request.referrer)

    return render_template('home/login.html')


@home_bp.route('/logout', methods=["GET"])
def logout():
    logout_user()
    flash("退出登录成功", 'info')
    return redirect(url_for('.login'))


@home_bp.route('/avatars/<path:filename>')
def get_avatar(filename):
    return send_from_directory(current_app.config['AVATARS_SAVE_PATH'], filename)
