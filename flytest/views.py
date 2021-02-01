#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from flask import current_app as app
from flask import flash, redirect, url_for, request
from flask import Blueprint, render_template, send_from_directory
from flask_login import current_user, login_user, logout_user, login_required
from .models import User, Product, Apiurl, Apitest, Apistep, Report, Bug
from .extensions import db
from .utils import redirect_back

fly = Blueprint('', __name__)


@fly.route('/')
@login_required
def index():
    return render_template('index.html', page_name='homepage')


@fly.route('/avatars/<path:filename>')
def get_avatar(filename):
    return send_from_directory(app.config['AVATARS_SAVE_PATH'], filename)


@fly.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get("password")
        remember = request.form.get("remember")
        if username and password:
            user = User.query.filter_by(email=username).first()
            if user and user.verify_password(password):
                login_user(user, remember=remember)
                flash("登录成功！", 'success')
                next_url = request.args.get('next', '.index')
                return redirect(url_for(next_url))
        flash('账户不存在', 'danger')
        return redirect(request.referrer)
    return render_template('login.html')


@fly.route('/logout')
@login_required
def logout():
    logout_user()
    flash("退出登录成功", 'info')
    return redirect(url_for('.login'))


@fly.route('/product', methods=["GET", "POST"])
@login_required
def product():
    if request.method == "POST":
        name = request.form.get('name')
        desc = request.form.get('desc')
        product_type = request.form.get('product_type')
        if not all([name, desc, product_type]):
            flash("添加产品失败", 'error')
            return redirect(request.referrer)
        product = Product(name=name, desc=desc, user=current_user)
        db.session.add(product)
        db.session.commit()
        return redirect(url_for('.product'))
    tags = (
        ('网页端', "网页端"),
        ('移动端', "移动端"),
        ('小程序', "小程序")
    )
    product = Product.query.first()
    page = request.args.get("page", 1)
    per_page = app.config['PER_PAGE_SIZE']
    paginate = Product.query.with_parent(current_user).order_by(
        Product.created.desc()).paginate(page, per_page)
    products = paginate.items
    return render_template('product.html', tags=tags, product=product, products=products,
                           paginate=paginate, page_name='productpage')


@fly.route('/env', methods=["GET", "POST"])
@fly.route('/env/<int:pk>', methods=["GET", "POST"])
@login_required
def env(pk=None):
    product = Product.query.get(pk) if pk else Product.query.first()
    if request.method == "POST":
        name = request.form.get('name')
        url = request.form.get('url')
        if name and url:
            apiurl = Apiurl(name=name, url=url, product=product)
            db.session.add(apiurl)
            db.session.commit()
            flash("【%s】%s添加成功" % (name, url), 'success')
            return redirect(url_for('.env', pk=pk))
        return redirect(request.referrer)
    page = request.args.get("page")
    per_page = app.config['PER_PAGE_SIZE']
    paginate = Apiurl.query.with_parent(product).order_by(
        Apiurl.created.desc()).paginate(page, per_page)
    envs = paginate.items
    return render_template('env.html', product=product,
                           envs=envs, paginate=paginate, page_name='envpage')


@fly.route('/test', methods=["GET", "POST"])
@fly.route('/test/<int:pk>', methods=["GET", "POST"])
@login_required
def test(pk=None):
    product = Product.query.get(pk) if pk else Product.query.first()
    if request.method == "POST":
        name = request.form.get('name')
        if name:
            apitest = Apitest(name=name, user=current_user, product=product)
            db.session.add(apitest)
            db.session.commit()
            return redirect(url_for('.test', pk=pk))
    page = request.args.get("page")
    per_page = app.config['PER_PAGE_SIZE']
    paginate = Apitest.query.with_parent(product).order_by(
        Apitest.created.desc()).paginate(page, per_page)
    tests = paginate.items
    return render_template('test.html', product=product, paginate=paginate,
                           tests=tests, page_name='testpage')


@fly.route('/step/<int:pk>', methods=["GET", "POST"])
def step(pk):
    apitest = Apitest.query.get(int(pk))
    if request.method == "POST":
        name = request.form.get('name')
        method = request.form.get('method')
        url = request.form.get('url')
        route = request.form.get('route')
        headers = request.form.get('headers')
        request_data = request.form.get('request_data')
        expected_result = request.form.get('expected_result')
        expected_regular = request.form.get('expected_regular')
        if not all([name, method, url]):
            flash("请输入完整的请求参数！")
            return redirect(request.referrer)
        apistep = Apistep(apitest=apitest, name=name, apiurl_id=url, method=method, request_data=request_data,
                          expected_result=expected_result, expected_regular=expected_regular)
        db.session.add(apistep)
        db.session.commit()
        return redirect(url_for('.step', pk=pk))
    page = request.args.get("page")
    per_page = app.config['PER_PAGE_SIZE']
    apiurl = Apiurl.query.filter_by(product_id=apitest.product_id).all()
    paginate = Apistep.query.filter_by(
        apitest=apitest).paginate(page, per_page)
    apisteps = paginate.items
    return render_template('step.html', apitest=apitest, apiurl=apiurl,
                           paginate=paginate, apisteps=apisteps, page_name='testpage')
