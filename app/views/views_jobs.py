#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from datetime import datetime
from flask import current_app
from flask import flash, redirect, url_for, request
from flask import Blueprint, render_template
from flask_login import login_required
from concurrent.futures import ThreadPoolExecutor
from app.models import Product, Apitest, Apistep, Work, CronTabTask

from app.choices import *
from app.utils import response_error, response_success, uid_name
from app.extensions import db, cache, raw_sql, scheduler
from app.tasks import api_step_job, api_test_job, crontab_job, saver_crontab


bp_job = Blueprint('job', __name__)


@bp_job.route('/work')
@bp_job.route('/work/<int:pk>')
@login_required
def work(pk=None):
    """工作视图"""
    product = Product.query.filter_by(id=pk, is_deleted=False).one_or_none() or Product.query.filter_by(is_deleted=False).first()
    if product is None:
        flash("请先创建一个项目", 'danger')
        return redirect(url_for('wx.product.product'))
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config['PER_PAGE_SIZE']
    pagination = Work.query.filter_by(product=product).order_by(Work.created.desc()).paginate(page, per_page)
    works = pagination.items
    return render_template('work.html', works=works, pagination=pagination, product=product, page_name='jobpage')



@bp_job.route('/jobs/<int:pd_id>/<int:t_id>')
@login_required
def jobs(pd_id, t_id):
    """场景测试"""
    apisteps = Apistep.query.filter_by(apitest_id=int(t_id), is_deleted=False).first()
    if apisteps is None:
        return response_error(1, "没有可以运行的步骤，请至少添加一个步骤")
    api_test_job.delay(int(t_id), 1)
    return response_success(data={"product": pd_id, "test": t_id})


@bp_job.route('/job/<int:pk>')
@login_required
def job(pk):
    """单步运行"""
    result = api_step_job.delay(int(pk))
    current_app.logger.info(result.wait())
    flash("正在运行测试步骤：%s" % pk, "info")
    return redirect(request.referrer)


@bp_job.route('/crons', methods=['GET', 'POST'])
@bp_job.route('/crons/<int:pk>', methods=['GET', 'POST'])
@login_required
def crontab_view(pk=None):
    """定时任务视图"""
    product = Product.query.filter_by(id=pk, is_deleted=False).one_or_none() or Product.query.filter_by(is_deleted=False).first()
    if product is None:
        flash("请先创建一个项目", 'danger')
        return redirect(url_for('wx.product.product'))
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config['PER_PAGE_SIZE']
    pagination = CronTabTask.query.filter_by(product_id=product.id, is_active=True).order_by(CronTabTask.start_date.desc()).paginate(page, per_page)
    crontabtask = pagination.items
    return render_template('crontab.html', crontab=CRONTAB, product=product, crontabtask=crontabtask, page_name='cronpage')


@bp_job.route('/crons/test/<int:pk>', methods=['POST'])
@login_required
def add_crontab_test(pk):
    """添加定时任务"""
    task_id = uid_name()
    trigger = request.form.get('trigger', type=str)
    jobsecond = request.form.get('jobsecond', type=int)
    apitest = Apitest.query.get_or_404(pk)
    if trigger == 'date':
        timesocend = datetime.strptime(jobsecond, "%Y-%m-%d %H:%M:%S")
        scheduler.add_job(id=task_id, func=crontab_job, args=(pk, ), trigger=trigger, run_date=timesocend)
    else:
        scheduler.add_job(id=task_id, func=crontab_job, args=(pk, ), trigger=trigger, seconds=jobsecond)
    if scheduler.get_job(task_id):
        req_url = request.url_root + "scheduler/jobs/" + task_id
        saver_crontab.delay(apitest.product_id, apitest.id, req_url)
    scheduler.state
    flash("添加定时任务成功", "success")
    return redirect(request.referrer)


@bp_job.get("/crontab/delete/<string:task_id>")
@login_required
def delete_crontab(task_id):
    current_app.logger.info("删除定时： %s成功"%task_id)
    obj = CronTabTask.query.filter_by(task_id=task_id).one_or_none()
    if obj is None :
        flash("任务不存在", 'danger')
        return redirect(request.referrer)
    obj.is_active=False
    db.session.commit()
    if scheduler.get_job(task_id):
        scheduler.remove_job(task_id)
    flash("删除任务%s成功"%task_id, "success")
    return redirect(url_for('.crontab_view'))