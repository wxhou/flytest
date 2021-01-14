#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from flask import Blueprint, request, render_template
from flask_login import current_user, login_required
from avatar.models import Product
from avatar.utils import per_page

pd_bp = Blueprint('product', __name__)


@pd_bp.route('/', methods=["GET"])
@login_required
def index():
    page = request.args.get("page")

    paginate = Product.query.filter_by(user_id=current_user.user.id).order_by(
        Product.created.desc()).paginate(page, per_page())
    products = paginate.items()
    return render_template('product/index.html',products=products)


@pd_bp.route('/add', methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        pass
    return render_template('product/add.html')
