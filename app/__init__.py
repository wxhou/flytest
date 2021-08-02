#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os
import logging
import click
from flask import Flask, render_template

from settings import BASE_DIR
from .extensions import (db, login_manager, avatars, migrate, moment, cache, scheduler)
from .models import User, Product, Apiurl, Apitest, Apistep, Report, Bug, Work


def create_app(env=None, celery=None):
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    app = Flask(__name__)
    print('use env is: %s' % env)
    _file = os.path.join(BASE_DIR, 'settings', env + '.py')
    app.config.from_pyfile(_file)
    register_extensions(app)
    if celery is not None:
        return app
    register_logger(app)
    register_blueprints(app)
    register_scheduler(app)
    register_template_context(app)
    register_shell_context(app)
    register_commands(app)
    register_errors(app)
    return app


def register_blueprints(app):
    from .views import bp_views  # 防止celery循环导入
    app.register_blueprint(bp_views, url_prefix='/')


def register_scheduler(app):
    scheduler.init_app(app)
    scheduler.start()


def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)
    avatars.init_app(app)
    migrate.init_app(app=app)
    moment.init_app(app)
    cache.init_app(app, app.config['CACHE_CONFIG'])


def register_template_context(app):
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    @app.context_processor
    def make_template_context():
        products = Product.query.filter_by(is_deleted=False)
        return dict(products=products)


def register_shell_context(app):

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


def register_commands(app):
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


def register_logger(app):
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
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors/400.html'), 400

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    @app.errorhandler(Exception)
    def internal_server_error(e):
        app.logger.error(format(e))
        return render_template('errors/500.html'), 500


if __name__ == "__main__":
    print(__name__)
