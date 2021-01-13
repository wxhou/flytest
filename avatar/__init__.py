#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os
import click
from flask import Flask
from avatar.settings import config
from avatar.extensions import (
    db
)
from avatar.views.view_index import index_bp


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    app.register_blueprint(index_bp, url_prefix='/')
    db.init_app(app)
    register_commands(app)
    return app


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


if __name__ == "__main__":
    print(create_app('development'))
