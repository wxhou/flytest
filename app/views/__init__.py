from flask import Blueprint
from .views_auth import bp_auth
from .views_environ import bp_environ
from .views_home import bp_home
from .views_itest import bp_test
from .views_jobs import bp_job
from .views_product import bp_product
from .views_report import bp_report


bp_views = Blueprint('wx', __name__)
bp_views.register_blueprint(bp_auth)
bp_views.register_blueprint(bp_environ)
bp_views.register_blueprint(bp_home)
bp_views.register_blueprint(bp_test)
bp_views.register_blueprint(bp_job)
bp_views.register_blueprint(bp_product)
bp_views.register_blueprint(bp_report)