try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin
import os
import json
import uuid
import time
from copy import deepcopy
from flask import current_app, jsonify
from flask import request, redirect, url_for


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


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


def response_error(code, msg=None):
    if msg is None:
        msg = 'error'
    return jsonify({'errcode': code, 'errmsg': msg})


def response_success(result=None, **kwargs):
    if result is None:
        res = {'data': result, 'errcode': 0, 'errmsg': 'success'}
    else:
        res = deepcopy(result)
    for k, v in kwargs.items():
        res[k] = v
    return jsonify(res)


def uid_name():
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, str(time.time())))


if __name__ == '__main__':
    print(uid_name())
