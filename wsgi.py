#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os
from flytest import create_app
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)

app = create_app('production')

