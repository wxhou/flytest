from flask import Blueprint, current_app, request, render_template, flash, redirect
from flask_login import login_required


bp_home = Blueprint('home', __name__)


@bp_home.route('/index')
@login_required
def index():
    return render_template('index.html', page_name='homepage')


@bp_home.route('/500')
def internet_error():
    return render_template('error/500.html')


@bp_home.route('/404.html')
def not_found():
    return render_template('error/404.html')


@bp_home.route('/search')
def search():
    q = request.args.get('q', '')
    if q == '':
        flash("请输入要搜索的内容！")
        return redirect(request.referrer)
    flash("该功能未开发！", "danger")
    return redirect(request.referrer)