from flask import request, current_app, Blueprint
from flask import flash, url_for , redirect, render_template
from flask_login import login_required, current_user
from app.models import Product, Apitest,Apistep, Apiurl
from app.choices import METHODS, CRONTAB
from app.core.extensions import db

bp_test = Blueprint('itest', __name__)



@bp_test.route('/test', methods=["GET", "POST"])
@bp_test.route('/test/<int:pk>', methods=["GET", "POST"])
@login_required
def test(pk=None):
    product = Product.get_product(pk)
    if product is None:
        flash("请先创建一个项目", 'danger')
        return redirect(url_for('wx.product.product'))
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
    pagination = Apitest.query.with_parent(product).filter_by(is_deleted=False).order_by(
        Apitest.created.desc()).paginate(page, per_page)
    tests = pagination.items
    return render_template('test.html', product=product, pagination=pagination,
                           tests=tests, crontab=CRONTAB, page_name='testpage')


@bp_test.route('/test/<int:pk>/edit', methods=["GET", "POST"])
@login_required
def edit_test(pk):
    apitest = Apitest.query.filter_by(id=pk, is_deleted=False).one_or_none()
    if request.method == "POST":
        name = request.form.get('name')
        apitest.name = name
        if request.form.get('delete'):
            apitest.is_deleted = True
        db.session.commit()
        return redirect(url_for('.test', pk=apitest.product_id))
    return render_template('test_edit.html', apitest=apitest, page_name='testpage')


@bp_test.route('/step/<int:pk>', methods=["GET", "POST"])
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
    apiurl = Apiurl.query.filter_by(product_id=apitest.product_id, is_deleted=False).all()
    pagination = Apistep.query.filter_by(
        apitest=apitest, is_deleted=False).paginate(page, per_page)
    apisteps = pagination.items
    return render_template('step.html', apitest=apitest, apiurl=apiurl, methods=METHODS,
                           pagination=pagination, apisteps=apisteps, page_name='testpage')


@bp_test.route('/step/<int:pk>/edit', methods=["GET", "POST"])
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
        if request.form.get("delete"):
            apistep.is_deleted = True
            current_app.logger.info("删除步骤： {}".format(apistep.name))
        db.session.commit()
        return redirect(url_for('.step', pk=apistep.apitest_id))
    current_app.logger.info("headers: {}".format(apistep.headers))
    current_app.logger.info("request_data: {}".format(apistep.request_data))
    return render_template('step_edit.html', apistep=apistep, apiurl=apiurl,
                           methods=METHODS, page_name='testpage')
