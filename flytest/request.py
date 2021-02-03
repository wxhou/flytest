import re
import json
import requests
from flask import current_app as app

from .extensions import db, cache
from .models import Report
from .utils import header_to_dict, generate_url


class HttpRequest(object):
    """HTTP request obj"""

    http_methods = 'get', 'post', 'put', 'delete'

    def __init__(self):
        self.r = requests.session()

    def request(self, case, task_id):
        """
        http request
        :param db:
        :param task_id:
        :return:
        """
        method = case.method
        url = generate_url(db.url, db.route)
        if header := case.headers:
            app.logger.info("请求头：%s" % header)
            cache.set('headers_%s' % task_id, header_to_dict(header))
        if data := case.request_data:
            cache.set('request_data_%s' % task_id, deserializer(data))
        app.logger.info("Request Url: {}".format(url))
        app.logger.info("Request Method: {}".format(method))
        app.logger.info("Request Headers: {}".format(
            cache.get('headers_%s' % task_id)))
        app.logger.info("Request Data: {}".format(
            cache.get('request_data_%s' % task_id)))
        response = self.dispatch(method.lower(), url,
                                 headers=cache.get('headers_%s' % task_id),
                                 **cache.get('request_data_%s' % task_id))
        _text = response.text
        app.logger.info("Response Data: {}".format(_text))
        expected_result = case.expected_result
        expected_regular = case.expected_regular
        status = check_result(_text, expected_result, expected_regular)
        app.logger.info("Test Result: {}".format("通过" if status else "失败"))
        case.results = _text
        case.status = status
        case.task_id = task_id
        db.session.commit()
        return response

    def dispatch(self, method, *args, **kwargs):
        """
        handler request
        :param method:
        :param args:
        :param kwargs:
        :return:
        """
        if method in self.http_methods:
            handler = getattr(self.r, method)
        else:
            handler = getattr(self.r, "get")
        return handler(*args, **kwargs)


def serializer(obj, ensure_ascii=True):
    """
        obj -> json_str
    """
    return json.dumps(obj, ensure_ascii=ensure_ascii)


def deserializer(json_str):
    """
        json_str -> obj
    """
    json_str = json_str.replace('\'', '\"')
    if is_json_str(json_str):
        return json.loads(json_str)
    return {}


def substitutions():
    """
    replace
    :return:
    """
    pass


def check_result(real_results, expected_result, expected_regular):
    """
    check_request_result
    :param real_results:
    :param expected_result:
    :param expected_regular:
    :return:
    """
    results = []
    if expected_result:
        result = expected_result in real_results
        results.append(result)
    if expected_regular:
        result = all(re.findall(r"%s" % expected_regular, real_results))
        results += result
    return 1 if all(results) else 0
