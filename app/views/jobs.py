#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from flask import current_app
from flask import flash, redirect, url_for, request, abort
from flask import Blueprint, render_template, send_from_directory
from flask_login import current_user, login_user, logout_user, login_required
from pyecharts import options as opts
from pyecharts.charts import Pie, Line

from app.models import (
    User, Product, Apiurl, Apitest, Apistep, Report, Bug, Work
)
from app.choices import *
from app.utils import uid_name, response_error, response_success
from app.extensions import db, cache, raw_sql, scheduler
from app.tasks import celery, apistep_job, apitest_job, testcaserunner_cron, teststeprunner_cron


bp_job = Blueprint('job', __name__)


@bp_job.route('/jobs/<int:pd_id>/<int:t_id>')
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


@bp_job.route('/job/<int:pk>')
@login_required
def job(pk):
    result = apistep_job.delay(int(pk))
    current_app.logger.info(result.wait())  # 65
    flash("正在运行测试步骤：%s" % pk, "info")
    return redirect(request.referrer)


@bp_job.route('/report')
@bp_job.route('/report/<int:pk>')
@login_required
def report(pk=None):
    product = Product.query.get_or_404(pk) if pk else Product.query.first()
    if product is None:
        flash("请先创建一个项目", 'danger')
        return redirect(url_for('.product'))
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
    raw_result = Report.query.group_by(
        Report.task_id).order_by(Report.created.desc())
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


@bp_job.route('/pie')
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


@bp_job.route('/bug')
@bp_job.route('/bug/<int:pk>')
@login_required
def bug(pk=None):
    product = Product.query.get_or_404(pk) if pk else Product.query.first()
    if product is None:
        flash("请先创建一个项目", 'danger')
        return redirect(url_for('.product'))
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


@bp_job.route('/trend')
@bp_job.route('/trend/<int:pk>')
@login_required
def trend(pk=None):
    product = Product.query.get_or_404(pk) if pk else Product.query.first()
    if product is None:
        flash("请先创建一个项目", 'danger')
        return redirect(url_for('.product'))
    return render_template('trending.html', page_name="trendpage", product=product)


@bp_job.route('/trending')
@bp_job.route('/trending/<int:pk>')
@login_required
def trending(pk=None):
    results = []
    raw_result = Report.query.group_by(
        Report.task_id).order_by(Report.created.desc())
    for res in raw_result:
        reports = Report.query.filter_by(task_id=res.id, is_deleted=False)
        apistep = Apistep.query.with_parent(res).first()
        test_name = 'unknown'
        if apistep:
            test_name = apistep.apitest.name
        results.append(
            [test_name, reports.filter_by(status=1).count(), reports.filter_by(status=0).count()])
    if results:
        current_app.logger.info(results)
        names, success, failure = zip(*results)
    else:
        names, success, failure = ['unknown'], [0], [0]
    current_app.logger.info(
        "名称：{}，通过：{}，失败：{}".format(names, success, failure))
    c = (
        Line(init_opts=opts.InitOpts(width="1000px", height="500px"))
        .add_xaxis(xaxis_data=names)
        .add_yaxis(
            series_name="失败数",
            y_axis=failure,
            is_smooth=True,
            is_connect_nones=True,
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
    ).dump_options_with_quotes()
    return c


@bp_job.route('/work')
@bp_job.route('/work/<int:pk>')
@login_required
def work(pk=None):
    product = Product.query.get_or_404(pk) if pk else Product.query.first()
    if product is None:
        flash("请先创建一个项目", 'danger')
        return redirect(url_for('.product'))
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config['PER_PAGE_SIZE']
    pagination = Work.query.filter_by(product=product).paginate(page, per_page)
    works = pagination.items
    return render_template('work.html', works=works, pagination=pagination, product=product, page_name='jobpage')


@bp_job.route('/crons', methods=['GET', 'POST'])
@bp_job.route('/crons/<int:pk>', methods=['GET', 'POST'])
@login_required
def crons(pk=None):
    product = Product.query.get_or_404(pk) if pk else Product.query.first()
    if product is None:
        flash("请先创建一个项目", 'danger')
        return redirect(url_for('.product'))
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


@bp_job.route('/crons/test/<int:pk>', methods=['POST'])
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


@bp_job.route('/crons/step/<int:pk>', methods=['POST'])
def crons2step(pk):
    task_id = uid_name()
    current_app.logger.info('task_id: {}'.format(task_id))
    trigger = request.form.get('trigger')
    jobsecond = request.form.get('jobsecond')
    scheduler.add_job(id=task_id, func=teststeprunner_cron, args=(pk, task_id),
                      trigger=trigger, minute=jobsecond)
    flash("添加定时任务成功", "success")
    return redirect(request.referrer)
