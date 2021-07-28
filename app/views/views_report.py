from pyecharts import options as opts
from pyecharts.charts import Pie, Line
from flask import Blueprint, flash, redirect, url_for, render_template, current_app, request, abort
from flask_login import login_required
from app.models import db, Product, Report, Apitest, Bug


bp_report = Blueprint('bp_report', __name__)



@bp_report.route('/report')
@bp_report.route('/report/<int:pk>')
@login_required
def report(pk=None):
    """测试报告"""
    # TODO:此函数执行SQL很多，需要优化
    product = Product.query.get_or_404(pk) if pk else Product.query.first()
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
    pagination = Report.query.order_by(Report.created.desc()).paginate(page, per_page)
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
    product = Product.query.get_or_404(pk) if pk else Product.query.first()
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
    product = Product.query.get_or_404(pk) if pk else Product.query.first()
    if product is None:
        flash("请先创建一个项目", 'danger')
        return redirect(url_for('wx.product.product'))
    return render_template('trending.html', page_name="trendpage", product=product)


@bp_report.route('/trending')
@bp_report.route('/trending/<int:pk>')
@login_required
def trending(pk=None):
    """趋势折线图"""
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
