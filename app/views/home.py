from flask import Blueprint, current_app, send_from_directory, render_template
from flask_login import login_required


bp_home = Blueprint('home', __name__)


@bp_home.route('/index')
@login_required
def index():
    return render_template('index.html', page_name='homepage')
