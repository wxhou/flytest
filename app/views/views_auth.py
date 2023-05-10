from io import BytesIO
from base64 import b64encode
from flask import request, current_app, Blueprint, send_from_directory, Response
from flask import flash, redirect, render_template, url_for
from flask_login import login_user, logout_user, login_required

from app.models import db, User
from app.extensions import cache
from app.utils import get_captcha, generate_token
from app.views.tasks import send_register_email


bp_auth = Blueprint('auth', __name__)


@bp_auth.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get("password")
        remember = request.form.get("remember")
        if username and password:
            user = User.query.filter_by(email=username, is_deleted=False).one_or_none()
            if not user:
                flash('账户不存在', 'danger')
                return redirect(request.referrer)
            if not user.is_active:
                flash('账户未激活！请先在邮箱中激活账户！', 'danger')
                return redirect(request.referrer)
            if user.verify_password(password):
                login_user(user, remember)
                next_url = request.args.get('next', url_for('wx.home.index'))
                flash("登录成功！", 'success')
                return redirect(next_url)
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
        captcha1 = request.form.get("captcha1")
        if not all([username, email, password1, password2, captcha1]):
            flash("请输入完整的注册信息！", 'danger')
            return redirect(request.referrer)
        if password1 != password2:
            flash("两次输入密码不相同", 'danger')
            return redirect(request.referrer)
        if cache.get("captcha_%s" % captcha1.strip()) is None:
            flash("验证码错误！", "danger")
            return redirect(request.referrer)
        user = User.query.filter_by(email=email).one_or_none()
        if user is not None:
            flash("该用户已存在，请登录", "warning")
            return redirect(url_for('wx.auth.login'))
        user = User(email=email, username=username, is_deleted=False)
        user.password = password1
        db.session.add(user)
        db.session.commit()
        token = generate_token(user.id)
        cache.set(token, user.id, timeout=7*24*60*60)
        register_url = url_for('wx.auth.active_user', token=token, _external=True)
        send_register_email.delay(register_url, user.email)
        flash("注册成功，请先在邮箱中激活用户后登陆！", "success")
        return redirect(url_for('wx.auth.login'))
    return render_template('register.html')


@bp_auth.get('/active/<token>')
def active_user(token):
    """激活用户"""
    user_id = cache.get(token)
    if not user_id:
        flash("验证码已过期，请重新注册！", "danger")
        db.session.delete(User.query.get(user_id))
        db.session.commit()
        return redirect(url_for('wx.auth.register'))
    user = User.query.filter_by(id=user_id, status=0, is_active=False).one_or_none()
    if user is None:
        flash("验证已过期，请重新注册！", "danger")
        return redirect(url_for('wx.auth.register'))
    user.is_active = True
    db.session.commit()
    cache.delete(token)
    flash("激活用户成功，请登录！", "success")
    return redirect(url_for('wx.auth.login'))


@bp_auth.get("/captcha.png")
def captcha():
    code, image = get_captcha(width=120, height=40)
    cache.set("captcha_%s" % code, code)
    buffer = BytesIO()
    image.save(buffer, format="png")
    resp = Response(buffer.getvalue(), mimetype="image/png")
    return resp
    # img_str = b64encode(buffer.getvalue()).decode()
    # return "data:image/png;base64," + img_str


@bp_auth.route('/avatars/<path:filename>')
@login_required
def get_avatar(filename):
    return send_from_directory(current_app.config['AVATARS_SAVE_PATH'], filename)
