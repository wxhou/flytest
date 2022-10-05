from flask import request, current_app, Blueprint, url_for
from flask import flash, redirect, render_template
from flask_login import login_required
from app.models import Product, Apiurl
from app.core.extensions import db

bp_environ = Blueprint('environ', __name__)


@bp_environ.route('/env', methods=["GET", "POST"])
@bp_environ.route('/env/<int:pk>', methods=["GET", "POST"])
@login_required
def env(pk=None):
    product = Product.get_product(pk)
    if product is None:
        flash("请先创建一个项目", 'danger')
        return redirect(url_for('wx.product.product'))
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
    pagination = Apiurl.query.with_parent(product).filter_by(is_deleted=False).order_by(
        Apiurl.created.desc()).paginate(page, per_page)
    env_res = dict(product=product,envs=pagination.items, page_name='envpage')
    if pagination.pages > 1:
        env_res['pagination']=pagination
    return render_template('env.html', **env_res)


@bp_environ.route('/env/<int:pk>/edit', methods=["GET", "POST"])
@login_required
def edit_env(pk):
    env = Apiurl.query.filter_by(id=int(pk), is_deleted=False).one_or_none()
    if request.method == 'POST':
        env.name = request.form.get('name')
        env.url = request.form.get('url')
        if request.form.get('delete'):
            env.is_deleted = True
        db.session.commit()
        return redirect(url_for('.env', pk=env.product_id))
    return render_template('env_edit.html', env=env, page_name='envpage')
