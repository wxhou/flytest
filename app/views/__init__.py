from flask import Blueprint
from .auth import bp_auth
from .environ import bp_environ
from .home import bp_home
from .itest import bp_test
from .jobs import bp_job
from .product import bp_product

bp_views = Blueprint('wx', __name__)
bp_views.register_blueprint(bp_auth)
bp_views.register_blueprint(bp_environ)
bp_views.register_blueprint(bp_home)
bp_views.register_blueprint(bp_test)
bp_views.register_blueprint(bp_job)
bp_views.register_blueprint(bp_product)
