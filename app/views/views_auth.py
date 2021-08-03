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


@bp_auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        if not all([username, email, password1, password2]):
            flash("请输入完整的注册信息！", 'danger')
            return redirect(request.referrer)
        if password1 != password2:
            flash("两次输入密码不相同", 'danger')
            return redirect(request.referrer)
        user = User.query.filter_by(email=email).one_or_none()
        if user is not None:
            flash("该用户已存在，请登录", "warning")
            return redirect(url_for('wx.auth.login'))
        user = User(email=email, username=username, is_deleted=False)
        user.password = password1
        db.session.add(user)
        db.session.commit()
        flash("注册成功请登录", "success")
        return redirect(url_for('wx.auth.login'))
    return render_template('register.html')


@bp_auth.route('/avatars/<path:filename>')
@login_required
def get_avatar(filename):
    return send_from_directory(current_app.config['AVATARS_SAVE_PATH'], filename)
