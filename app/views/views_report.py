import pygal
from pygal.style import Style
from flask import Blueprint, flash, redirect, url_for, render_template, current_app, request, abort
from flask_login import login_required
from app.models import db, Product, Report, Apitest, Bug


bp_report = Blueprint('bp_report', __name__)


@bp_report.route('/report')
@bp_report.route('/report/<int:pk>')
@login_required
def report(pk=None):
    """测试报告"""
    product = Product.get_product(pk)
    if product is None:
        flash("请先创建一个项目", 'danger')
        return redirect(url_for('wx.product.product'))    
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config['PER_PAGE_SIZE']
    task_id = request.args.get('task_id')
    query_filter = [Report.is_deleted==False]
    if task_id := request.args.get('task_id'):
        query_filter.append(Report.task_id==task_id)
    pagination = Report.query.with_parent(product).filter(*query_filter).order_by(
        Report.created.desc()).paginate(page, per_page)
    reports = pagination.items
    results = {}
    for report in reports:
        if report.task_id not in results:
            results[report.task_id] = {
                "pk": report.id,
                "task_id": report.task_id,
                "name": report.name,
                "success": 0,
                "failure": 0,
                "updated": report.updated,
                "types": report.types
            }
        if report.status == 1:
            results[report.task_id]['success'] += 1
        else:
            results[report.task_id]['failure'] += 1
    if not results:
        flash("没有找到对应的报告！", "danger")
        return redirect(request.referrer)
    report_result = dict(results=results.values(), product=product, page_name='reportpage')
    if pagination.pages > 1:
        report_result["pagination"] = pagination
    return render_template('report.html', **report_result)


@bp_report.route('/bug')
@bp_report.route('/bug/<int:pk>')
@login_required
def bug(pk=None):
    product = Product.get_product(pk)
    if product is None:
        flash("请先创建一个项目", 'danger')
        return redirect(url_for('wx.product.product'))
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


@bp_report.route('/trend')
@bp_report.route('/trend/<int:pk>')
@login_required
def trend(pk=None):
    """趋势视图"""
    product = Product.get_product(pk)
    if product is None:
        flash("请先创建一个项目", 'danger')
        return redirect(url_for('wx.product.product'))
    names, success, failure = ['unknown'], [0], [0]
    results = {}
    reports = Report.query.order_by(Report.created.desc()).limit(10)
    for report in reports:
        if report.task_id not in results:
            results[report.task_id] = [report.name, 0, 0]
        if report.status == 1:
            results[report.task_id][1] += 1
        else:
            results[report.task_id][2] += 1
    if results:
        names, success, failure = zip(*results.values())
    line_chart = pygal.Line(
        x_label_rotation=20, interpolate='hermite', style=Style(colors=('green', 'red')))
    line_chart.title = "测试结果趋势图"
    line_chart.x_labels = names
    line_chart.add("通过数", success)
    line_chart.add("失败数", failure)
    chart = line_chart.render_data_uri()
    return render_template('trending.html', chart=chart, page_name="trendpage", product=product)