try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin
import os
import json
from flask import current_app
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
    current_app.logger.info(res)
    return dict(res)


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


if __name__ == '__main__':
    pass
