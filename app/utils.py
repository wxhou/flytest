import os
import json
import uuid
import time
from copy import deepcopy
from urllib.parse import urljoin
from flask import jsonify, current_app


def generate_url(url, route):
    """
    generate url
    :param url:
    :param route:
    :return:
    """
    current_app.logger.info("请求服务器：{}".format(url))
    current_app.logger.info("请求路径：`{}`".format(route))
    if not route:
        return url.strip()
    return urljoin(url.strip(), route.strip())


def header_to_dict(raw_str):
    """header to dict
    :type raw_str: str
    """
    if '\\n' in raw_str:
        raw_str = raw_str.split('\\n')
    else:
        raw_str = raw_str.split('\n')
    res = [[k.strip() for k in i.split(": ")] for i in raw_str]
    return dict(res)


def params2dict(raw_str):
    """get params to dict
    """
    if isinstance(raw_str, dict):
        return raw_str
    new_dict = dict(i.split('=') for i in raw_str.split('&'))
    return new_dict


def is_json_str(string):
    """str is json str
    """
    if isinstance(string, str):
        try:
            data = json.loads(string)
            return data
        except ValueError:
            return False
    return False


def make_dir(dir):
    if '.' in dir:
        dir = os.path.dirname(dir)
    if os.path.exists(dir):
        return dir
    else:
        os.makedirs(dir)
        return dir


def response_error(code, msg="None"):
    return jsonify({'errcode': code, 'errmsg': msg})


def response_success(**kwargs):
    res = {'errcode': 0, 'errmsg': '任务正在运行！'}
    for k, v in kwargs.items():
        res[k] = v
    return jsonify(res)


def uid_name():
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, str(time.time())))


if __name__ == '__main__':
    print(uid_name())
