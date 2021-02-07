#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from flask import current_app
from flask import flash, redirect, url_for, request
from flask import Blueprint, render_template, send_from_directory
from flask_login import current_user, login_user, logout_user, login_required
from .models import (
    User, Product, Apiurl, Apitest, Apistep, Report, Bug
)
from .extensions import db, cache, raw_sql
from .utils import redirect_back
from .choices import *
from .tasks import apistep_job, apitest_job
from pyecharts import options as opts
from pyecharts.charts import Pie, Line


fly = Blueprint('', __name__)


@fly.route('/index')
@login_required
def index():
    return render_template('index.html', page_name='homepage')


@fly.route('/avatars/<path:filename>')
def get_avatar(filename):
    return send_from_directory(current_app.config['AVATARS_SAVE_PATH'], filename)


@fly.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get("password")
        remember = request.form.get("remember")
        if username and password:
            user = User.query.filter_by(email=username).first()
            if user and user.verify_password(password):
                login_user(user, remember)
                flash("登录成功！", 'success')
                return redirect_back()
        flash('账户不存在', 'danger')
        return redirect(request.referrer)
    return render_template('login.html')


@fly.route('/logout')
@login_required
def logout():
    logout_user()
    flash("退出登录成功", 'success')
    return redirect(url_for('.login'))


@fly.route('/product', methods=["GET", "POST"])
@login_required
def product():
    if request.method == "POST":
        name = request.form.get('name')
        desc = request.form.get('desc')
        product_type = request.form.get('product_type')
        if not all([name, desc, product_type]):
            flash("添加产品失败", 'danger')
            return redirect(request.referrer)
        product = Product(name=name, desc=desc, tag=product_type,
                          user=current_user, is_deleted=False)
        db.session.add(product)
        db.session.commit()
        return redirect(url_for('.product'))
    tags = (
        ('网页端', "网页端"),
        ('移动端', "移动端"),
        ('小程序', "小程序")
    )
    page = request.args.get("page", 1)
    per_page = current_app.config['PER_PAGE_SIZE']
    paginate = Product.query.with_parent(current_user).order_by(
        Product.created.desc()).paginate(page, per_page)
    products = paginate.items
    return render_template('product.html', tags=tags, products=products,
                           paginate=paginate, page_name='productpage')


@fly.route('/product/<int:pk>/edit', methods=["GET", "POST"])
@login_required
def edit_product(pk):
    product = Product.query.get_or_404(pk)
    if request.method == 'POST':
        name = request.form.get('name')
        desc = request.form.get('desc')
        delete = request.form.get('delete')
        product_type = request.form.get('product_type')
        if not product_type:
            flash("没有产品类型", 'danger')
            return redirect(request.referrer)
        product.name = name
        product.desc = desc
        product.tag = product_type
        if delete:
            product.is_deleted = True
        db.session.commit()
        flash("更新项目信息成功！", "success")
        return redirect(url_for('.product'))
    return render_template('product_edit.html', product=product, tags=TAGS, page_name='productpage')


@fly.route('/env', methods=["GET", "POST"])
@fly.route('/env/<int:pk>', methods=["GET", "POST"])
@login_required
def env(pk=None):
    product = Product.query.get(pk) if pk else Product.query.first()
    if request.method == "POST":
        name = request.form.get('name')
        url = request.form.get('url')
        if name and url:
            apiurl = Apiurl(name=name, url=url,
                            product=product, is_deleted=False)
            db.session.add(apiurl)
            db.session.commit()
            flash("【%s】%s添加成功" % (name, url), 'success')
            return redirect(url_for('.env', pk=pk))
        return redirect(request.referrer)
    page = request.args.get("page")
    per_page = current_app.config['PER_PAGE_SIZE']
    paginate = Apiurl.query.with_parent(product).order_by(
        Apiurl.created.desc()).paginate(page, per_page)
    envs = paginate.items
    return render_template('env.html', product=product,
                           envs=envs, paginate=paginate, page_name='envpage')


@fly.route('/env/<int:pk>/edit', methods=["GET", "POST"])
@login_required
def edit_env(pk):
    env = Apiurl.query.get_or_404(pk)
    if request.method == 'POST':
        name = request.form.get('name')
        url = request.form.get('url')
        delete = request.form.get('delete')
        env.name = name
        env.url = url
        if delete:
            env.is_deleted = True
        db.session.commit()
        return redirect(url_for('.env', pk=env.product_id))
    return render_template('env_edit.html', env=env, page_name='envpage')


@fly.route('/test', methods=["GET", "POST"])
@fly.route('/test/<int:pk>', methods=["GET", "POST"])
@login_required
def test(pk=None):
    product = Product.query.get(pk) if pk else Product.query.first()
    if request.method == "POST":
        name = request.form.get('name')
        if name:
            apitest = Apitest(name=name, user=current_user,
                              product=product, is_deleted=False)
            db.session.add(apitest)
            db.session.commit()
            return redirect(url_for('.test', pk=pk))
        else:
            flash("没有输入用例名称")
            return redirect(request.referrer)
    page = request.args.get("page")
    per_page = current_app.config['PER_PAGE_SIZE']
    paginate = Apitest.query.with_parent(product).order_by(
        Apitest.created.desc()).paginate(page, per_page)
    tests = paginate.items
    return render_template('test.html', product=product, paginate=paginate,
                           tests=tests, page_name='testpage')


@fly.route('/test/<int:pk>/edit', methods=["GET", "POST"])
@login_required
def edit_test(pk):
    apitest = Apitest.query.get_or_404(pk)
    if request.method == "POST":
        name = request.form.get('name')
        delete = request.form.get('delete')
        apitest.name = name
        if delete:
            apitest.is_deleted = True
        db.session.commit()
        return redirect(url_for('.test', pk=apitest.product_id))
    return render_template('test_edit.html', apitest=apitest, page_name='testpage')


@fly.route('/step/<int:pk>', methods=["GET", "POST"])
@login_required
def step(pk):
    apitest = Apitest.query.get_or_404(int(pk))
    if request.method == "POST":
        name = request.form.get('name')
        method = request.form.get('method')
        url = request.form.get('url')
        route = request.form.get('route')
        headers = request.form.get('headers')
        request_data = request.form.get('request_data')
        expected_result = request.form.get('expected_result')
        expected_regular = request.form.get('expected_regular')
        extract = request.form.get('extract')
        if not all([name, method, url]):
            flash("请输入完整的请求参数！", 'warning')
            return redirect(request.referrer)
        apistep = Apistep(apitest=apitest, name=name, apiurl_id=url, route=route,
                          method=method, request_data=request_data, headers=headers,
                          expected_result=expected_result, expected_regular=expected_regular,
                          extract=extract, is_deleted=False)
        db.session.add(apistep)
        db.session.commit()
        return redirect(url_for('.step', pk=pk))
    page = request.args.get("page")
    per_page = current_app.config['PER_PAGE_SIZE']
    apiurl = Apiurl.query.filter_by(product_id=apitest.product_id).all()
    paginate = Apistep.query.filter_by(
        apitest=apitest).paginate(page, per_page)
    apisteps = paginate.items
    return render_template('step.html', apitest=apitest, apiurl=apiurl, methods=METHODS,
                           paginate=paginate, apisteps=apisteps, page_name='testpage')


@fly.route('/step/<int:pk>/edit', methods=["GET", "POST"])
@login_required
def edit_step(pk):
    apiurl = Apiurl.query.filter_by(is_deleted=False)
    apistep = Apistep.query.get_or_404(pk)
    if request.method == "POST":
        name = request.form.get('name')
        apistep.name = name
        apistep.method = request.form.get('method')
        apistep.url = request.form.get('url')
        apistep.route = request.form.get('route')
        apistep.headers = request.form.get('headers')
        apistep.request_data = request.form.get('request_data')
        apistep.expected_result = request.form.get('expected_result')
        apistep.expected_regular = request.form.get('expected_regular')
        apistep.extract = request.form.get('extract')
        flash("更新步骤【{}】成功".format(name), 'success')
        db.session.commit()
        return redirect(url_for('.step', pk=apistep.apitest_id))
    current_app.logger.info("headers: {}".format(apistep.headers))
    current_app.logger.info("request_data: {}".format(apistep.request_data))
    return render_template('step_edit.html', apistep=apistep, apiurl=apiurl,
                           methods=METHODS, page_name='testpage')


@fly.route('/jobs/<int:pk>')
@login_required
def jobs(pk):
    apitest_job.delay(int(pk))
    flash("正在运行测试用例：%s" % pk, 'info')
    return redirect(request.referrer)


@fly.route('/job/<int:pk>')
@login_required
def job(pk):
    apistep_job.delay(int(pk))
    flash("正在运行测试步骤：%s" % pk, "info")
    return redirect(request.referrer)


@fly.route('/report')
@login_required
def report():
    task_id = request.args.get('task_id')
    if task_id:
        reports = Report.query.filter_by(task_id=task_id, is_deleted=False)
        current_app.logger.info(reports)
        first_report = reports.first()
        content = {
            "pk": first_report.id,
            "task_id": task_id,
            "name": first_report.name,
            "success": reports.filter_by(status=1).count(),
            "failure": reports.filter_by(status=0).count(),
            "updated": first_report.updated
        }
        return render_template('report.html', results=content, first_task=task_id, page_name='reportpage')
    first_task = None
    results = []
    raw_result = raw_sql(
        'SELECT task_id,COUNT(task_id) from report GROUP BY task_id ORDER BY created desc;')
    for res in raw_result:
        reports = Report.query.filter_by(task_id=res[0], is_deleted=False)
        first_report = reports.first()
        if first_task is None:
            first_task = first_report.task_id
        content = {
            "pk": first_report.id,
            "task_id": first_report.task_id,
            "name": first_report.name,
            "success": reports.filter_by(status=1).count(),
            "failure": reports.filter_by(status=0).count(),
            "updated": first_report.updated
        }
        results.append(content)
    current_app.logger.info("报告数据：{}".format(results))
    return render_template('report.html', results=results, first_task=first_task, page_name='reportpage')


@fly.route('/pie')
@login_required
def pie():
    task_id = request.args.get('task_id')
    current_app.logger.info("pie图task_id是：%s" % task_id)
    if not task_id:
        return {}, 400
    reports = Report.query.filter_by(task_id=task_id, is_deleted=False)
    c = (
        Pie()
        .add("", [["测试失败", reports.filter_by(status=0).count()],
                  ["测试成功", reports.filter_by(status=1).count()]])
        .set_colors(["red", "green"])
        .set_global_opts(title_opts=opts.TitleOpts(title="最新报告"))
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
    )
    return c.dump_options_with_quotes()


@fly.route('/bug')
@login_required
def bug():
    bugs = Bug.query.filter_by(is_deleted=False).order_by(Bug.updated.desc())
    return render_template('bug.html',bugs=bugs, page_name='bugpage')


@fly.route('/trend')
@login_required
def trend():
    return render_template('trending.html', page_name="trendpage")


@fly.route('/trending')
@login_required
def trending():
    results = []
    raw_result = raw_sql(
        'SELECT task_id,COUNT(task_id) from report GROUP BY task_id;')
    for res in raw_result:
        reports = Report.query.filter_by(task_id=res[0], is_deleted=False)
        first_report = reports.first()
        apistep = Apistep.query.with_parent(first_report).first()
        if apistep:
            test_name = apistep.apitest.name
        else:
            test_name = 'default'
        results.append(
            [test_name, reports.filter_by(status=1).count(), reports.filter_by(status=0).count()])
    current_app.logger.info("results内容：{}".format(results))
    if results:
        names, success, failure = zip(*results)
    else:
        names, success, failure = ['default'], [0], [0]
    current_app.logger.info(
        "名称：{}，通过：{}，失败：{}".format(names, success, failure))
    c = (
        Line()
        .add_xaxis(names)
        .add_yaxis("失败", failure, color="red")
        .add_yaxis("通过", success, color="green")
        .set_global_opts(title_opts=opts.TitleOpts(title="测试结果趋势图"))
    )
    return c.dump_options_with_quotes()
