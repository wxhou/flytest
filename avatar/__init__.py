#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os
import click
from flask import Flask
from avatar.settings import config
from avatar.extensions import (
    db, login_manager, debugtoolbar, avatars, migrate
)
from avatar.models import User, Product, Apiurl, Apitest, Apistep
from avatar.views.view_home import home_bp


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    register_blueprints(app)
    register_extensions(app)
    register_commands(app)
    return app


def register_blueprints(app):
    app.register_blueprint(home_bp, url_prefix='/')


def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)
    debugtoolbar.init_app(app)
    avatars.init_app(app)
    migrate.init_app(app)


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
        """Building Bluelog, just for you."""

        click.echo('Initializing the database...')
        db.create_all()

        admin = User.query.first()
        if admin is not None:
            click.echo('The administrator already exists, updating...')
            admin.email = email
            admin.password = password
        else:
            click.echo('Creating the temporary administrator account...')
            admin = User(
                email=email,
                nickname='avatar',
            )
            admin.password = password
            db.session.add(admin)
        db.session.commit()
        click.echo('Done.')


if __name__ == "__main__":
    print(create_app('development'))
