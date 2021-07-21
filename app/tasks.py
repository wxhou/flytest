import time
from celery.utils.log import get_task_logger
from .extensions import db, scheduler
from .models import Apistep, Apitest, Report, Bug
from .request import HttpRequest
from .utils import generate_url
from .worker import celery

log = get_task_logger(__name__)


def testcaserunner(pk, task_id, jobtype=1):
    """运行测试用例"""
    print("开始测试用例" + str(pk))
    apitest = Apitest.query.get_or_404(pk)
    apisteps = Apistep.query.filter_by(apitest=apitest, is_deleted=False)
    for step in apisteps:
        HttpRequest().http_request(step, task_id)
    apisteps = Apistep.query.filter_by(apitest_id=pk)
    results = []
    for i in apisteps:
        report = Report(task_id=task_id, name=apitest.name, product_id=apitest.product_id,
                        result=i.results, status=i.status, is_deleted=False, types=jobtype)
        db.session.add(report)
        report.apistep = i
        if i.status == 0:
            bug = Bug(task_id=task_id, casename=i.apitest.name, stepname=i.name, product_id=apitest.product_id,
                      request="""
                        请求方法：{}
                        请求地址：{}
                        请求内容：{}
                        """.format(i.method, generate_url(i.apiurl.url, i.route), i.request_data),
                      detail="""
                    {} 不在预期结果中
                    实际响应：{}
                    """.format(i.expected_result + '&' + i.expected_regular, i.results),
                      status=i.status,
                      is_deleted=False)
            db.session.add(bug)
        results.append(i.status)
    status = all(results)
    apitest.task_id = task_id
    apitest.results = 1 if status else 0
    db.session.commit()
    print("结束测试用例" + str(pk))


def testcaserunner_cron(pk, task_id):
    with scheduler.app.app_context():
        testcaserunner(pk, task_id, jobtype=2)


def teststeprunner(pk, task_id):
    """测试步骤运行"""
    apistep = Apistep.query.get(pk)
    HttpRequest().http_request(apistep, task_id)
    if Apistep.query.filter_by(apitest_id=apistep.apitest_id).count() == 1:
        apitest = Apitest.query.get(apistep.apitest_id)
        apitest.task_id = task_id
        apitest.results = apistep.status
        db.session.commit()


def teststeprunner_cron(pk, task_id):
    with scheduler.app.app_context():
        teststeprunner(pk, task_id)


@celery.task
def apistep_job(pk):
    task_id = apistep_job.request.id
    hostname = apistep_job.request.hostname
    teststeprunner(pk, task_id)
    task_info = celery.control.inspect().active()
    return task_info[hostname]


@celery.task
def apitest_job(pk):
    task_id = apitest_job.request.id
    hostname = apitest_job.request.hostname
    testcaserunner(pk, task_id)
    task_info = celery.control.inspect().active()
    return task_info[hostname]