import time
import requests
from celery.utils.log import get_task_logger
from .extensions import db, scheduler
from .models import Apistep, Apitest, Report, Bug, CronTabTask
from .request import HttpRequest
from .utils import generate_url
from .worker import celery

log = get_task_logger(__name__)

###########
# Celery任务
###########


@celery.task
def api_step_job(pk):
    """单步运行"""
    task_id = api_step_job.request.id
    hostname = api_step_job.request.hostname
    # StepTestJob
    apistep = Apistep.query.get(pk)
    HttpRequest().http_request(apistep, task_id)
    if Apistep.query.filter_by(apitest_id=apistep.apitest_id).count() == 1:
        apitest = Apitest.query.get(apistep.apitest_id)
        apitest.task_id = task_id
        apitest.results = apistep.status
        db.session.commit()
    # StepTestJobEnd
    task_info = celery.control.inspect().active()
    return task_info[hostname]


@celery.task
def api_test_job(pk, types):
    """多步运行或场景测试"""
    task_id = api_test_job.request.id
    hostname = api_test_job.request.hostname
    # CeleryCaseTestJob
    log.info("开始测试用例" + str(pk))
    apitest = Apitest.query.get_or_404(pk)
    apisteps = Apistep.query.filter_by(apitest=apitest, is_deleted=False)
    for step in apisteps:
        HttpRequest().http_request(step, task_id)
    results = []
    for i in apisteps:
        report = Report(task_id=task_id, name=apitest.name, product_id=apitest.product_id,
                        result=i.results, status=i.status, is_deleted=False, types=types)
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
    log.info("测试结果状态results： {}".format(results))
    status = all(results)
    apitest.task_id = task_id
    apitest.results = 1 if status else 0
    db.session.commit()
    log.info("结束测试用例" + str(pk))
    # CeleryCaseTestJobEnd
    task_info = celery.control.inspect().active()
    return task_info[hostname]


############
# 定时任务
############
# 1、interval
# 间隔任务
# 2、cron
# 定时任务，指定时间触发任务
# 3、date
# 一次性任务
############


def crontab_job(pk):
    """定时任务"""
    api_test_job.delay(pk, 2)


@celery.task
def saver_crontab(pk, t_id, url):
    """保存定时任务信息"""
    r = requests.get(url).json()
    times = f'{r.get("hours", 0)}时{r.get("minutes", 0)}分{r.get("seconds", 0)}秒'
    res = {
        "task_id": r.get("id"),
        "func_name": r.get("func"),
        "trigger": r.get("trigger"),
        "args": r.get("args"),
        "kwargs": r.get("kwargs"),
        "max_instances": r.get("max_instances"),
        "times": times,
        "misfire_grace_time": r.get("misfire_grace_time"),
        "next_run_time": r.get("next_run_time"),
        "start_date": r.get("start_date"),
        "product_id": pk
    }
    if apitest := Apitest.query.get(t_id):
        res['test_name'] = apitest.name
    obj = CronTabTask(**res)
    db.session.add(obj)
    db.session.commit()
