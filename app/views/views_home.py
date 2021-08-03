from flask import Blueprint, current_app, request, render_template, flash, redirect
from flask_login import login_required


bp_home = Blueprint('home', __name__)


@bp_home.route('/index')
@login_required
def index():
    return render_template('index.html', page_name='homepage')


@bp_home.route('/search')
def search():
    q = request.args.get('q', '')
    if q == '':
        flash("请输入要搜索的内容！")
        return redirect(request.referrer)
    