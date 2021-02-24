#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from flask import current_app
from flask import flash, redirect, url_for, request, abort
from flask import Blueprint, render_template, send_from_directory
from flask_login import current_user, login_user, logout_user, login_required
from .models import (
    User, Product, Apiurl, Apitest, Apistep, Report, Bug, Work
)
from flytest.choices import *
from flytest.utils import uid_name, response_error, response_success
from flytest.extensions import db, cache, raw_sql, scheduler
from flytest.tasks import celery, apistep_job, apitest_job, testcaserunner_cron, teststeprunner_cron
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
                next_url = request.args.get('next', url_for('.index'))
                flash("登录成功！", 'success')
                return redirect(next_url)
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
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config['PER_PAGE_SIZE']
    pagination = Product.query.with_parent(current_user).order_by(
        Product.created.desc()).paginate(page, per_page)
    products = pagination.items
    return render_template('product.html', tags=TAGS, products=products,
                           pagination=pagination, page_name='productpage')


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
    product = Product.query.get_or_404(pk) if pk else Product.query.first()
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
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config['PER_PAGE_SIZE']
    pagination = Apiurl.query.with_parent(product).order_by(
        Apiurl.created.desc()).paginate(page, per_page)
    envs = pagination.items
    return render_template('env.html', product=product,
                           envs=envs, pagination=pagination, page_name='envpage')


@fly.route('/env/<int:pk>/edit', methods=["GET", "POST"])
@login_required
def edit_env(pk):
    env = Apiurl.query.get_or_404(pk)
    if request.method == 'POST':
        env.name = request.form.get('name')
        env.url = request.form.get('url')
        delete = request.form.get('delete')
        if delete:
            env.is_deleted = True
        db.session.commit()
        return redirect(url_for('.env', pk=env.product_id))
    return render_template('env_edit.html', env=env, page_name='envpage')


@fly.route('/test', methods=["GET", "POST"])
@fly.route('/test/<int:pk>', methods=["GET", "POST"])
@login_required
def test(pk=None):
    product = Product.query.get_or_404(pk) if pk else Product.query.first()
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
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config['PER_PAGE_SIZE']
    pagination = Apitest.query.with_parent(product).order_by(
        Apitest.created.desc()).paginate(page, per_page)
    tests = pagination.items
    return render_template('test.html', product=product, pagination=pagination,
                           tests=tests, crontab=CRONTAB, page_name='testpage')


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
        request_extract = request.form.get('request_extract')
        response_extract = request.form.get('response_extract')
        if not all([name, method, url]):
            flash("请输入完整的请求参数！", 'warning')
            return redirect(request.referrer)
        apistep = Apistep(apitest=apitest, name=name, apiurl_id=url, route=route,
                          method=method, request_data=request_data, headers=headers,
                          expected_result=expected_result, expected_regular=expected_regular,
                          request_extract=request_extract, response_extract=response_extract, is_deleted=False)
        db.session.add(apistep)
        db.session.commit()
        return redirect(url_for('.step', pk=pk))
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config['PER_PAGE_SIZE']
    apiurl = Apiurl.query.filter_by(product_id=apitest.product_id).all()
    pagination = Apistep.query.filter_by(
        apitest=apitest).paginate(page, per_page)
    apisteps = pagination.items
    return render_template('step.html', apitest=apitest, apiurl=apiurl, methods=METHODS,
                           pagination=pagination, apisteps=apisteps, page_name='testpage')


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
        apistep.request_extract = request.form.get('request_extract')
        apistep.response_extract = request.form.get('response_extract')
        flash("更新步骤【{}】成功".format(name), 'success')
        db.session.commit()
        return redirect(url_for('.step', pk=apistep.apitest_id))
    current_app.logger.info("headers: {}".format(apistep.headers))
    current_app.logger.info("request_data: {}".format(apistep.request_data))
    return render_template('step_edit.html', apistep=apistep, apiurl=apiurl,
                           methods=METHODS, page_name='testpage')


@fly.route('/jobs/<int:pd_id>/<int:t_id>')
@login_required
def jobs(pd_id, t_id):
    result = apitest_job.delay(int(t_id))
    res = result.wait()
    # current_app.logger.info(result)
    # current_app.logger.info(result.id)
    # current_app.logger.info(result.info)
    for i in res:
        work = Work(task_id=result.id,
                    name=apitest_job.name,
                    params="{}&{}".format(i['args'], i['kwargs']),
                    hostname=i['hostname'],
                    status=result.status,
                    result=str(result.get(timeout=1)),
                    traceback=result.traceback,
                    product_id=pd_id
                    )
        db.session.add(work)
    db.session.commit()
    return response_success(data={"product": pd_id, "test": t_id})


@fly.route('/job/<int:pk>')
@login_required
def job(pk):
    result = apistep_job.delay(int(pk))
    current_app.logger.info(result.wait())  # 65
    flash("正在运行测试步骤：%s" % pk, "info")
    return redirect(request.referrer)


@fly.route('/report')
@fly.route('/report/<int:pk>')
@login_required
def report(pk=None):
    product = Product.query.get_or_404(pk) if pk else Product.query.first()
    task_id = request.args.get('task_id')
    if task_id:
        reports = Report.query.filter_by(
            product=product, task_id=task_id, is_deleted=False)
        current_app.logger.info(reports)
        first_report = reports.first()
        if first_report is None:
            abort(404)
        content = {
            "pk": first_report.id,
            "task_id": task_id,
            "name": first_report.name,
            "success": reports.filter_by(status=1).count(),
            "failure": reports.filter_by(status=0).count(),
            "updated": first_report.updated
        }
        return render_template('report.html', results=[content], first_task=task_id, product=product,
                               page_name='reportpage')
    first_task = None
    results = []
    raw_result = Report.query.group_by(Report.task_id).order_by(Report.created.desc())
    for res in raw_result:
        reports = Report.query.filter_by(task_id=res.task_id, is_deleted=False)
        if first_task is None:
            first_task = res.task_id
        content = {
            "pk": res.id,
            "task_id": res.task_id,
            "name": res.name,
            "success": reports.filter_by(status=1).count(),
            "failure": reports.filter_by(status=0).count(),
            "updated": res.updated
        }
        results.append(content)
    current_app.logger.info("报告数据：{}".format(results))
    return render_template('report.html', results=results, first_task=first_task,
                           product=product, page_name='reportpage')


@fly.route('/pie')
@login_required
def pie():
    task_id = request.args.get('task_id')
    current_app.logger.info("pie图task_id是：%s" % task_id)
    if not task_id:
        return {}, 400
    reports = Report.query.filter_by(task_id=task_id, is_deleted=False)
    c = (
        Pie(
            init_opts=opts.InitOpts(
                width="200px",
                height="200px"
            )
        )
        .add(
            series_name="",
            data_pair=[["测试失败", reports.filter_by(status=0).count()],
                       ["测试成功", reports.filter_by(status=1).count()]],
            radius='50%',
        )
        .set_colors(["red", "green"])
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="最新报告",
            ))
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
    )
    return c.dump_options_with_quotes()


@fly.route('/bug')
@fly.route('/bug/<int:pk>')
@login_required
def bug(pk=None):
    product = Product.query.get_or_404(pk) if pk else Product.query.first()
    task_id = request.args.get('task_id')
    if task_id:
        bugs = Bug.query.filter_by(product=product,
                                   task_id=task_id, is_deleted=False).order_by(Bug.updated.desc())

        return render_template('bug.html', bugs=bugs, product=product, page_name='bugpage')
    else:
        page = request.args.get("page", 1, type=int)
        per_page = current_app.config['PER_PAGE_SIZE']
        pagination = Bug.query.filter_by(product=product,
                                         is_deleted=False).order_by(Bug.updated.desc()).paginate(page, per_page)
        bugs = pagination.items
        return render_template('bug.html', pagination=pagination, bugs=bugs, product=product, page_name='bugpage')


@fly.route('/trend')
@fly.route('/trend/<int:pk>')
@login_required
def trend(pk=None):
    product = Product.query.get_or_404(pk) if pk else Product.query.first()
    return render_template('trending.html', page_name="trendpage", product=product)


@fly.route('/trending')
@fly.route('/trending/<int:pk>')
@login_required
def trending(pk=None):
    results = []
    raw_result = Report.query.group_by(Report.task_id).order_by(Report.created.desc())
    for res in raw_result:
        reports = Report.query.filter_by(task_id=res.id, is_deleted=False)
        apistep = Apistep.query.with_parent(res).first()
        if apistep:
            test_name = apistep.apitest.name
        else:
            test_name = 'null'
        results.append(
            [test_name, reports.filter_by(status=1).count(), reports.filter_by(status=0).count()])
    if results:
        names, success, failure = zip(*results)
    else:
        names, success, failure = ['null'], [0], [0]
    current_app.logger.info(
        "名称：{}，通过：{}，失败：{}".format(names, success, failure))
    c = (
        Line(init_opts=opts.InitOpts(width="1000px", height="500px"))
        .add_xaxis(xaxis_data=names)
        .add_yaxis(
            series_name="失败数",
            is_smooth=True,
            is_connect_nones=True,
            y_axis=failure,
            markpoint_opts=opts.MarkPointOpts(
                data=[
                    opts.MarkPointItem(type_="max", name="最大值"),
                    opts.MarkPointItem(type_="min", name="最小值"),
                ]
            ),
            markline_opts=opts.MarkLineOpts(
                data=[opts.MarkLineItem(type_="average", name="平均值")]
            ),
        )
        .add_yaxis(
            series_name="通过数",
            y_axis=success,
            is_smooth=True,
            is_connect_nones=True,
            markpoint_opts=opts.MarkPointOpts(
                data=[opts.MarkPointItem(value=-2, name="周最低", x=1, y=-1.5)]
            ),
            markline_opts=opts.MarkLineOpts(
                data=[
                    opts.MarkLineItem(type_="average", name="平均值"),
                    opts.MarkLineItem(symbol="none", x="90%", y="max"),
                    opts.MarkLineItem(
                        symbol="circle", type_="max", name="最高点"),
                ]
            ),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="趋势图"),
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
            toolbox_opts=opts.ToolboxOpts(is_show=True),
            xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False),
        )
    )
    return c.dump_options_with_quotes()


@fly.route('/work')
@fly.route('/work/<int:pk>')
@login_required
def work(pk=None):
    product = Product.query.get_or_404(pk) if pk else Product.query.first()
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config['PER_PAGE_SIZE']
    pagination = Work.query.filter_by(product=product).paginate(page, per_page)
    works = pagination.items
    return render_template('work.html', works=works, pagination=pagination, product=product, page_name='jobpage')


@fly.route('/crons', methods=['GET', 'POST'])
@fly.route('/crons/<int:pk>', methods=['GET', 'POST'])
@login_required
def crons(pk=None):
    product = Product.query.get_or_404(pk) if pk else Product.query.first()
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config['PER_PAGE_SIZE']
    pagination = Apitest.query.with_parent(product).filter_by(
        is_deleted=False).paginate(page, per_page)
    apitests = pagination.items
    if request.method == "POST":
        trigger = request.form.get('trigger')
        jobsecond = request.form.get('jobsecond')
        add_cronjob2test.delay(pk, trigger=trigger, minute=jobsecond)
        return redirect(url_for('.crons', pk=pk))
    return render_template('crons.html', crontab=CRONTAB, product=product, page_name='cronpage')


@fly.route('/crons/test/<int:pk>', methods=['POST'])
@login_required
def crons2test(pk):
    task_id = uid_name()
    current_app.logger.info('task_id: {}'.format(task_id))
    trigger = request.form.get('trigger')
    jobsecond = request.form.get('jobsecond')
    scheduler.add_job(id=task_id, func=testcaserunner_cron, args=(pk, task_id),
                      trigger=trigger, minute=jobsecond)
    flash("添加定时任务成功", "success")
    return redirect(request.referrer)


@fly.route('/crons/step/<int:pk>', methods=['POST'])
def crons2step(pk):
    task_id = uid_name()
    current_app.logger.info('task_id: {}'.format(task_id))
    trigger = request.form.get('trigger')
    jobsecond = request.form.get('jobsecond')
    scheduler.add_job(id=task_id, func=teststeprunner_cron, args=(pk, task_id),
                      trigger=trigger, minute=jobsecond)
    flash("添加定时任务成功", "success")
    return redirect(request.referrer)
