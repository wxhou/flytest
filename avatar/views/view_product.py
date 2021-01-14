#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from flask import Blueprint, request, render_template


pd_bp = Blueprint('product', __name__)


@pd_bp.route('/', methods=["GET"])
def index():
    return render_template('product/index.html')


@pd_bp.route('/add', methods=["GET", "POST"])
def add():
    if request.method == "POST":
        pass
    return render_template('product/add.html')
