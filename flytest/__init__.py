#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os
import click
from flask import Flask
from celery import Celery
from .extensions import (
    db, login_manager, avatars, migrate, moment, toolbar, cache
)
from flytest.models import User, Product, Apiurl, Apitest, Apistep, Report, Bug
from flytest.settings import config, cache_config, WIN
from flytest.celeryconfig import broker_url, result_backend

celery = Celery(__name__, broker=broker_url, backend=result_backend)


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True
    register_blueprints(app)
    register_extensions(app)
    register_template_context(app)
    register_shell_context(app)
    register_commands(app)
    register_celery(app)
    return app


def register_celery(app):
    celery.config_from_object('flytest.celeryconfig')

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask


def register_blueprints(app):
    from flytest.views import fly  # 防止celery循环导入
    app.register_blueprint(fly, url_prefix='/')


def register_extensions(app):
    login_manager.init_app(app)
    avatars.init_app(app)
    migrate.init_app(app=app)
    moment.init_app(app)
    cache.init_app(app, config=cache_config)
    db.init_app(app)
    if not WIN:
        toolbar.init_app(app)


def register_template_context(app):
    @app.context_processor
    def make_template_context():
        products = Product.query.all()
        return dict(products=products)


def register_shell_context(app):
    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db, User=User, Product=Product,
                    Apiurl=Apiurl, Apitest=Apitest, Apistep=Apistep,
                    Report=Report, Bug=Bug)


def register_commands(app):
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop.')
    def initdb(drop):
        """Initialize the database."""
        if drop:
            click.confirm(
                'This operation will delete the database, do you want to continue?', abort=True)
            db.drop_all()
            click.echo('Drop tables.')
        db.create_all()
        click.echo('Initialized database.')

    @app.cli.command()
    @click.option('--email', prompt=True, help='The email to login.')
    @click.option('--password', prompt=True, hide_input=True,
                  confirmation_prompt=True, help='The password used to login.')
    def adminuser(email, password):
        click.echo('Initializing the database...')
        db.create_all()

        admin = User.query.first()
        if admin is not None:
            click.echo('The administrator already exists, updating...')
            admin.email = email
            admin.password = password
        else:
            click.echo('Creating the temporary administrator account...')
            admin = User(email=email, username='admin')
            admin.password = password
            db.session.add(admin)
        db.session.commit()
        click.echo('Administrator Created Done.')


if __name__ == "__main__":
    print(__name__)
