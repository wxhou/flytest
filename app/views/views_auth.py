from flask import request, current_app, Blueprint, send_from_directory
from flask import flash, redirect, render_template, url_for
from flask_login import login_user, logout_user, login_required

from app.models import db, User


bp_auth = Blueprint('auth', __name__)


@bp_auth.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get("password")
        remember = request.form.get("remember")
        if username and password:
            user = User.query.filter_by(email=username).first()
            if user and user.verify_password(password):
                login_user(user, remember)
                next_url = request.args.get('next', url_for('wx.home.index'))
                flash("登录成功！", 'success')
                return redirect(next_url)
        flash('账户不存在', 'danger')
        return redirect(request.referrer)
    return render_template('login.html')


@bp_auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash("退出登录成功", 'success')
    return redirect(url_for('wx.auth.login'))


@bp_auth.route('/avatars/<path:filename>')
def get_avatar(filename):
    return send_from_directory(current_app.config['AVATARS_SAVE_PATH'], filename)
