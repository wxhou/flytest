from flask import request, current_app, Blueprint
from flask import flash, redirect, render_template
from flask_login import login_required
from app.models import Product, Apiurl

bp_environ = Blueprint('environ', __name__)


@bp_environ.route('/env', methods=["GET", "POST"])
@bp_environ.route('/env/<int:pk>', methods=["GET", "POST"])
@login_required
def env(pk=None):
    product = Product.query.get_or_404(pk) if pk else Product.query.first()
    if product is None:
        flash("请先创建一个项目", 'danger')
        return redirect(url_for('.product'))
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


@bp_environ.route('/env/<int:pk>/edit', methods=["GET", "POST"])
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
