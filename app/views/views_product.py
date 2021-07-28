from flask import request, current_app, Blueprint
from flask import url_for, flash, redirect, render_template
from flask_login import login_required, current_user
from app.choices import *
from app.models import Product
from app.extensions import db

bp_product = Blueprint('product', __name__)


@bp_product.route('/product', methods=["GET", "POST"])
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
        return redirect(url_for('wx.product.product'))
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config['PER_PAGE_SIZE']
    pagination = Product.query.with_parent(current_user).order_by(
        Product.created.desc()).paginate(page, per_page)
    products = pagination.items
    return render_template('product.html', tags=TAGS, products=products,
                           pagination=pagination, page_name='productpage')


@bp_product.route('/product/<int:pk>/edit', methods=["GET", "POST"])
@login_required
def edit_product(pk):
    product = Product.query.get_or_404(pk)
    if product is None:
        flash("请先创建一个项目", 'danger')
        return redirect(url_for('wx.product.product'))
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
        return redirect(url_for('wx.product.product'))
    return render_template('product_edit.html', product=product, tags=TAGS, page_name='productpage')

