try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin
import json
from flask import current_app as app
from flask import request, redirect, url_for


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def redirect_back(default='.index', **kwargs):
    for target in request.args.get('next'), request.referrer:
        if target:
            return redirect(target)
    return redirect(url_for(default, **kwargs))


def generate_url(url, route):
    """
    generate url
    :param url:
    :param route:
    :return:
    """
    if route is None:
        return url
    return urljoin(url.rstrip('/'),
                   route if route[0] == '/' else '/' + route)


def header_to_dict(raw_str):
    """header to dict
    :type raw_str: str
    """
    return dict([k.strip() for k in i.split(": ", 1)] for i in raw_str.split('\n'))


def is_json_str(string):
    """str is json str
    """
    if not isinstance(string, str):
        return False
    try:
        data = json.loads(string)
        return data
    except ValueError:
        return False
