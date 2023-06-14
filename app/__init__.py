import os
import logging
import platform
import atexit
import click
from flask import Flask, render_template
from flask_login import current_user
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from app.extensions import (db, login_manager, avatars, register_celery, limiter,
                         migrate, moment, mail, cache, scheduler)
from app.models import User, Product, Apiurl, Apitest, Apistep, Report, Bug, Work


def create_app(**kwargs):
    env = os.getenv('FLASK_ENV') or 'development'
    app = Flask(__name__,
                template_folder='./templates',
                static_folder='./static')
    print('use env is: %s' % env)
    _file = os.path.join(app.root_path, 'settings', env + '.py')
    app.config.from_pyfile(_file)
    register_extensions(app)
    register_celery(celery=kwargs.get('celery'), app=app)
    register_logger(app)
    register_blueprints(app)
    register_scheduler(app)
    register_template_context(app)
    register_shell_context(app)
    register_commands(app)
    register_errors(app)
    return app


def register_blueprints(app: Flask):
    from app.views import bp_views
    app.register_blueprint(bp_views, url_prefix='/')


def register_scheduler(app: Flask):
    """
    保证系统只启动一次定时任务
    :param app:
    :return:
    """
    app.config['SCHEDULER_JOBSTORES'] = {
            'default': SQLAlchemyJobStore(url=app.config['SQLALCHEMY_DATABASE_URI'])
        }
    if platform.system() != 'Windows':
        fcntl = __import__("fcntl")
        f = open('scheduler.lock', 'wb')
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            scheduler.init_app(app)
            scheduler.start()
            app.logger.debug('Scheduler Started,---------------')
        except:
            pass

        def unlock():
            fcntl.flock(f, fcntl.LOCK_UN)
            f.close()

        atexit.register(unlock)
    else:
        msvcrt = __import__('msvcrt')
        f = open('scheduler.lock', 'wb')
        try:
            msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
            scheduler.init_app(app)
            scheduler.start()
            app.logger.debug('Scheduler Started,----------------')
        except:
            pass

        def _unlock_file():
            try:
                f.seek(0)
                msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
            except:
                pass

        atexit.register(_unlock_file)


def register_extensions(app: Flask):
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    avatars.init_app(app)
    migrate.init_app(app=app)
    moment.init_app(app)
    cache.init_app(app, app.config['CACHE_CONFIG'])
    limiter.init_app(app)


def register_template_context(app: Flask):
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    @app.context_processor
    def make_template_context():
        result = {}
        if current_user.is_authenticated:
            products = Product.query.filter_by(
                user=current_user, is_deleted=False)
            result['products'] = products
        return result


def register_shell_context(app: Flask):

    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db,
                    User=User,
                    Product=Product,
                    Apiurl=Apiurl,
                    Apitest=Apitest,
                    Apistep=Apistep,
                    Report=Report,
                    Bug=Bug,
                    Work=Work)


def register_commands(app: Flask):
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop.')
    def initdb(drop):
        """Initialize the database.
        if you update tables. then delete a table before to create_all.
        """
        if drop:
            click.confirm(
                'This operation will delete the database, do you want to continue?',
                abort=True)
            db.drop_all()
            click.echo('Drop tables.')
        db.create_all()
        click.echo('Initialized database.')

    @app.cli.command()
    @click.option('--email', prompt=True, help='The email to login.')
    @click.option('--password',
                  prompt=True,
                  hide_input=True,
                  confirmation_prompt=True,
                  help='The password used to login.')
    def adminuser(email, password):
        admin = User.query.first()
        if admin is not None:
            click.echo('The administrator already exists, updating...')
            admin.email = email
            admin.password = password
        else:
            click.echo('Creating the temporary administrator account...')
            admin = User(email=email, username='admin', is_deleted=False)
            admin.password = password
            db.session.add(admin)
        db.session.commit()
        click.echo('Administrator Created Done.')

    @app.cli.command()
    @click.option('--email', prompt=True, help='The email to login.')
    @click.option('--password',
                  prompt=True,
                  hide_input=True,
                  confirmation_prompt=True,
                  help='The password used to login.')
    def adduser(email, password):
        click.echo('Creating the temporary user account...')
        user = User(email=email, username='user', is_deleted=False)
        user.password = password
        db.session.add(user)
        db.session.commit()
        click.echo('User Created Done.')


def register_logger(app: Flask):
    from logging.handlers import RotatingFileHandler

    app.logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s')
    file_handler = RotatingFileHandler(filename=app.config['FLASK_LOGGER_FILE'],
                                       maxBytes=10 * 1024 * 1024,
                                       backupCount=10)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    app.logger.addHandler(file_handler)


def register_errors(app: Flask):

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    @app.errorhandler(Exception)
    def internal_server_error(e):
        import traceback
        app.logger.critical(traceback.format_exc())
        return render_template('errors/500.html'), 500
