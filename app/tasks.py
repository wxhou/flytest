import time
import requests
from celery.result import AsyncResult
from celery.utils.log import get_task_logger
from celery.signals import task_success, task_failure
from .extensions import db, scheduler
from .models import Apistep, Apitest, Work, Report, Bug, CronTabTask
from .request import HttpRequest
from .utils import generate_url
from .worker import celery, flask_app

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


@celery.task(bind=True)
def api_test_job(self, pk, types):
    """多步运行或场景测试"""
    task_id = self.request.id
    log.info("开始测试用例" + str(pk))
    apitest = Apitest.query.filter_by(id=int(pk), is_deleted=False).one_or_none()
    if apitest is None:
        return None
    work = Work(task_id=task_id,
            name=self.name,
            params="{}&{}".format(self.request.args, self.request.kwargs),
            hostname=self.request.hostname,
            status="PENDING",
            product_id=apitest.product_id
            # result=str(result.get(timeout=1)),
            # traceback=result.traceback,
            )
    db.session.add(work)
    db.session.commit()
    # CeleryCaseTestJob
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
    status = results and all(results)
    apitest.task_id = task_id
    apitest.results = 1 if status else 0
    db.session.commit()
    log.info("结束测试用例" + str(pk))
    # CeleryCaseTestJobEnd
    # task_info = celery.control.inspect().active()
    # task_info[self.request.hostname]
    return "{}测试成功！".format(apitest.name)  


@task_success.connect(sender=api_test_job)
def task_success_test(sender=None, **kwargs):
    with flask_app.app_context():
        """任务成功处理"""
        task_res = AsyncResult(sender.request.id)
        work = Work.query.filter_by(task_id=task_res.task_id).one_or_none()
        if work is not None:
            work.status = task_res.state
            work.result = task_res.result
            db.session.commit()


@task_failure.connect(sender=api_test_job)
def task_failure_test(sender=None, **kwargs):
    """任务失败处理"""
    with flask_app.app_context():
        task_res = AsyncResult(sender.request.id)
        work = Work.query.filter_by(task_id=task_res.task_id).one_or_none()
        if work is not None:
            work.result = task_res.info
            work.status = task_res.state
            work.traceback = task_res.traceback
            db.session.commit()

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
