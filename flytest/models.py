#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_login import UserMixin
from flytest.extensions import db
from flask_avatars import Identicon


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True)
    username = db.Column(db.String(128))
    password_hash = db.Column(db.String(128))
    avatar_s = db.Column(db.String(64))
    avatar_m = db.Column(db.String(64))
    avatar_l = db.Column(db.String(64))
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow,
                        default=datetime.utcnow)

    products = db.relationship('Product', back_populates='user')
    apitests = db.relationship('Apitest', back_populates='user')

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        self.generate_avatar()

    def generate_avatar(self):
        avatar = Identicon()
        filenames = avatar.generate(text=self.email)
        self.avatar_s = filenames[0]
        self.avatar_m = filenames[1]
        self.avatar_l = filenames[2]
        db.session.commit()

    @property
    def password(self):
        return AttributeError("password is only readable")

    @password.setter
    def password(self, pwd):
        self.password_hash = generate_password_hash(pwd)

    def verify_password(self, pwd):
        return check_password_hash(self.password_hash, pwd)

    def __repr__(self):
        return self.username


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    desc = db.Column(db.Text)
    tag = db.Column(db.String(32))
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow,
                        default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='products')

    apiurls = db.relationship('Apiurl', back_populates='product')
    apitests = db.relationship('Apitest', back_populates='product')

    def __repr__(self):
        return '<Product %s>' % self.name


class Apiurl(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    url = db.Column(db.String(512))
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow,
                        default=datetime.utcnow)

    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    product = db.relationship('Product', back_populates="apiurls")
    apisteps = db.relationship('Apistep', back_populates='apiurl')

    def __repr__(self):
        return '<Url %s>' % self.name


class Apitest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    results = db.Column(db.Integer, default=-1)
    task_id = db.Column(db.String(255), index=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow,
                        default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='apitests')
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    product = db.relationship('Product', back_populates='apitests')
    apisteps = db.relationship('Apistep', back_populates='apitest')

    def __repr__(self):
        return '<ApiTest %s>' % self.name


class Apistep(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    method = db.Column(db.String(16))
    request_data = db.Column(db.Text, nullable=True)
    expected_result = db.Column(db.String(512))
    expected_regular = db.Column(db.String(512), nullable=True)
    status = db.Column(db.Boolean)
    results = db.Column(db.String(512), nullable=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow,
                        default=datetime.utcnow)

    apiurl_id = db.Column(db.Integer, db.ForeignKey('apiurl.id'))
    apiurl = db.relationship('Apiurl', back_populates='apisteps')
    apitest_id = db.Column(db.Integer, db.ForeignKey('apitest.id'))
    apitest = db.relationship('Apitest', back_populates='apisteps')
    report_id = db.Column(db.Integer, db.ForeignKey("report.id"))
    report = db.relationship('Report', back_populates='apisteps')

    def __repr__(self):
        return '<ApiStep %s>' % self.name


class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(255), index=True)
    result = db.Column(db.String(2048))
    status = db.Column(db.Integer, default=-1)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow,
                        default=datetime.utcnow)

    apisteps = db.relationship('Apistep', back_populates='report')

    def __repr__(self):
        return self.apisteps


class Bug(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(255), index=True)
    casename = db.Column(db.String(256))
    stepname = db.Column(db.String(512))
    request = db.Column(db.Text)
    detail = db.Column(db.Text)
    status = db.Column(db.Integer, default='未解决')
    level = db.Column(db.String(10), default='一般')
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow,
                        default=datetime.utcnow)

    def __repr__(self):
        return '<BUG FOR %S>' % self.stepname
