import pygal
from flask import Blueprint, Markup, flash, redirect, url_for, render_template, current_app, request, abort
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
    task_id = request.args.get('task_id')
    if task_id:
        reports = Report.query.filter_by(product=product, task_id=task_id, is_deleted=False)
        content = {}
        for report in reports:
            if report.task_id not in content:
                content["task_id"] = report.task_id
                content["name"] = report.name
                content["success"] = 0
                content["failure"] = 0
                content["updated"] = report.updated
            if report.status == 1:
                content['success'] += 1
            else:
                content['failure'] += 1
        return render_template('report.html', results=[content], first_task=task_id, product=product,
                               page_name='reportpage')
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config['PER_PAGE_SIZE']
    results = {}
    first_task = None
    pagination = Report.query.with_parent(product).order_by(Report.created.desc()).paginate(page, per_page)
    reports = pagination.items
    for report in reports:
        current_app.logger.info(report.created)
        if first_task is None:
            first_task = report.task_id
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
    return render_template('report.html', results=results.values(), first_task=first_task,
                           product=product,pagination=pagination, page_name='reportpage')


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


@bp_report.route('/pie')
@login_required
def pie():
    """饼状图"""
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
    line_chart = pygal.Line(x_label_rotation=20, interpolate='hermite')
    line_chart.title = "测试结果趋势图"
    line_chart.x_labels = names
    line_chart.add("通过数", success)
    line_chart.add("失败数", failure)
    chart = line_chart.render_data_uri()
    return render_template('trending.html', chart=chart, page_name="trendpage", product=product)