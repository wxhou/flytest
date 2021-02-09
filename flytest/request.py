import re
import json
from string import Template
from requests.sessions import Session
from flask import current_app

from .extensions import db, cache
from .utils import header_to_dict, params2dict, generate_url, is_json_str


class BaseRequest(Session):
    http_methods = 'get', 'post', 'put', 'delete'

    def __init__(self):
        super(BaseRequest, self).__init__()
        self.re = re

    def compiles(self, string):
        """regular_compile
        """
        return re.compile(string)

    def set_cache(self, k, v):
        cache.set(k, v)

    def delete_cache(self, k):
        cache.delete(k)

    def get_cache(self, k):
        if data := cache.get(k):
            return data
        return {}

    def serializer(self, obj, ensure_ascii=True):
        """
            obj -> json_str
        """
        return json.dumps(obj, ensure_ascii=ensure_ascii)

    def deserializer(self, json_str):
        """
            json_str -> obj
        """
        json_str = json_str.replace("'", '"')
        if data := is_json_str(json_str):
            if "params" in data:
                data['params'] = params2dict(data['params'])
            return data
        elif isinstance(json_str, dict):
            return json_str
        else:
            current_app.logger.error("请求内容不是json字符串格式，请检查")
            current_app.logger.error(json_str)
            return {}

    def substitutions(self, raw_str, task_id):
        """
        replace
        :return:
        """
        pattern = self.compiles(r'\${(.*?)}')
        result = pattern.findall(raw_str)
        if not result:
            current_app.logger.info("没有需要替换的变量！")
            return raw_str
        replace = {name: self.get_cache(
            "%s_%s" % (name, task_id)) for name in result}
        current_app.logger.info("需要替换的变量: {}".format(replace))
        new_str = Template(raw_str).safe_substitute(**replace)
        current_app.logger.info("替换后的文本：{}".format(new_str))
        return new_str

    def check_result(self, real_results, expected_result, expected_regular):
        """
        check_request_result
        :param real_results:
        :param expected_result:
        :param expected_regular:
        :return:
        """
        results = []
        if expected_result:
            current_app.logger.info("预期结果：{}".format(expected_result))
            result = expected_result in real_results
            current_app.logger.info("预期结果是否通过：{}".format(result))
            results.append(result)
        if expected_regular:
            current_app.logger.info("预期正则：{}".format(expected_regular))
            pattern = self.compiles(r'%s' % expected_regular)
            result = all(pattern.findall(real_results))
            current_app.logger.info('预期正则是否通过：{}'.format(expected_regular))
            results += result
        res = 1 if all(results) else 0
        current_app.logger.info("是否通过：{}".format(res))
        return res


class HttpRequest(BaseRequest):
    """HTTP request obj"""

    def http_request(self, case, task_id):
        """
        http request
        :param db:
        :param task_id:
        :return:
        """
        method = case.method
        url = generate_url(case.apiurl.url, case.route)
        if header := case.headers:
            header = header.strip().replace("：", ": ")
            header = self.substitutions(header, task_id)
            self.set_cache('headers_%s' % task_id, header_to_dict(header))
        if data := case.request_data:
            data = data
            data = self.substitutions(data, task_id)
            # request_extract
            if extract := case.request_extract:
                self.get_extract(data, extract, task_id)
            self.set_cache('request_data_%s' %
                           task_id, self.deserializer(data))
        else:
            self.delete_cache('request_data_%s' % task_id)
        # logging
        current_app.logger.info("请求方法：%s" % method)
        current_app.logger.info("请求地址: {}".format(url))
        current_app.logger.info("请求头: {}".format(
            self.get_cache('headers_%s' % task_id)))
        current_app.logger.info("请求内容: {}".format(
            self.get_cache('request_data_%s' % task_id)))
        # request
        response = self.dispatch(method.lower(), url,
                                 headers=self.get_cache(
                                     'headers_%s' % task_id),
                                 **self.get_cache('request_data_%s' % task_id))
        # response
        _text = response.text
        case.results = _text
        current_app.logger.info("响应内容: {}".format(_text))
        # check_result
        expected_result = case.expected_result
        expected_regular = case.expected_regular
        status = self.check_result(_text, expected_result, expected_regular)
        current_app.logger.info("步骤[{}]测试结果: {}".format(
            case.name, "通过" if status else "失败"))
        case.status = status
        # response_extract
        if extract := case.response_extract:
            self.get_extract(_text, extract, task_id)
        db.session.commit()
        current_app.logger.info(">>" * 45)
        return response

    def get_extract(self, to_string, extract, task_id):
        extracts = extract.split('|')
        current_app.logger.info("需获取的变量值列表：{}".format(extracts))
        for name in extracts:
            thename = '\"%s":.*?"(.*?)"' % name
            current_app.logger.info("表达式：{}".format(thename))
            pattern = self.compiles(r'{}'.format(thename))
            result = pattern.findall(to_string)
            current_app.logger.info("获取变量[{}]的值：{}".format(name, result))
            name = "%s_%s" % (name, task_id)
            self.set_cache(name, result[0])
            current_app.logger.info("变量【%s】值设置结果：%s" %
                                    (name, self.get_cache(name)))

    def dispatch(self, method, *args, **kwargs):
        """handler request
        :param method:
        :param args:
        :param kwargs:
        :return:
        """
        if method in self.http_methods:
            handler = getattr(self, method)
        else:
            handler = getattr(self, "get")
        return handler(*args, **kwargs)
