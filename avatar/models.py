#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from avatar.extensions import db


class BaseModel(db.Model):
    """模型基类"""
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow)


class User(BaseModel, UserMixin):
    # __tablename__ = 'tp_user'
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(10))
    email = db.Column(db.String(128), unique=True)
    password_hash = db.Column(db.String(128))
    products = db.relationship('Product', backref='user', lazy=True)  # pass
    apitests = db.relationship('Apitest', backref='user', lazy=True)

    @property
    def password(self):
        return AttributeError("password not readable")

    @password.setter
    def password(self, pwd):
        self.password_hash = generate_password_hash(pwd)

    def verify_password(self, pwd):
        return check_password_hash(self.password_hash, pwd)

    def __repr__(self) -> str:
        return '<User %s>' % self.name


class Product(BaseModel):
    """项目"""
    # __tablename__ = 'tp_product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    desc = db.Column(db.Text)
    tag = db.Column(db.String(32))
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.id'), nullable=False)  # pass
    apiurls = db.relationship('Apiurl', backref='product', lazy=True)  # pass
    apitests = db.relationship('Apitest', backref='product', lazy=True)  # pass

    def __repr__(self) -> str:
        return '<Product %s>' % self.name


class Apiurl(BaseModel):
    """测试地址"""
    # __tablename__ = 'tp_apiurl'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey(
        'product.id'), nullable=False)  # pass
    name = db.Column(db.String(128), unique=True)
    url = db.Column(db.String(512))
    apisteps = db.relationship("Apistep", backref='apiurl', lazy=True)  # pass

    def __repr__(self) -> str:
        return '<Url %s>' % self.name


class Apitest(BaseModel):
    """流程测试"""
    # __tablename__ = 'tp_apitest'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey(
        'product.id'), nullable=False)  # pass
    apisteps = db.relationship("Apistep", backref='apitest', lazy=True)  # pass
    results = db.Column(db.Text)

    def __repr__(self):
        return '<ApiTest %s>' % self.name


class Apistep(BaseModel):
    """测试步骤"""
    # __tablename__ = 'tp_apistep'
    id = db.Column(db.Integer, primary_key=True)
    apitest_id = db.Column(db.Integer, db.ForeignKey(
        "apitest.id"), nullable=False)  # pass
    name = db.Column(db.String(128))
    apiurl_id = db.Column(db.Integer, db.ForeignKey('apiurl.id'), nullable=False)  # pass
    method = db.Column(db.String(16))
    params = db.Column(db.Text, nullable=True)
    body = db.Column(db.Text, nullable=True)
    expected_result = db.Column(db.String(512))
    expected_regular = db.Column(db.String(512), nullable=True)
    status = db.Column(db.Boolean)
    results = db.Column(db.String(512), nullable=True)

    def __repr__(self):
        return '<ApiStep %s>' % self.name