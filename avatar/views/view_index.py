#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import request

index_bp = Blueprint('', __name__)


@index_bp.route('/')
def index():
    return "hello flask"
