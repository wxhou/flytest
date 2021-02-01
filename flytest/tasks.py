from flask import current_app as app
from flytest import celery
from .extensions import db
from flytest.models import Apistep, Apitest, Report, Bug
from flytest.request import HttpRequest
from .utils import generate_url


@celery.task()
def apistep_job(pk):
    apistep = Apistep.query.get(pk)
    task_id = apistep_job.request.id
    HttpRequest().request(apistep, task_id)
    if Apistep.query.filter_by(apitest_id=apistep.apitest_id).count() == 1:
        apitest = Apitest.query.get(apistep.apitest_id)
        apitest.task_id = task_id
        apitest.results = apistep.status
        db.session.commit()


@celery.task()
def apitest_job(pk):
    task_id = apitest_job.request.id
    apisteps = Apistep.query.filter_by(apitest_id=pk)
    for step in apisteps:
        HttpRequest().request(step, task_id)
    app.logger.info("测试完成！")
    apisteps = Apistep.query.filter_by(apitest_id=pk)
    results = []
    for i in apisteps:
        if i.status == 0:
            bug = Bug(task_id=task_id, casename=i.apitest.name, stepname=i.name,
                      request="""
                        请求方法：{}
                        请求地址：{}
                        请求内容：{}
                        """.format(i.method, generate_url(i.url, i.route), i.request_data),
                      detail="""
                      预期结果：{}
                      实际结果：{}
                      """.format(i.expected_result, i.results),
                      status=i.status)
            db.session.add(bug)
        results.append(i.status)
    status = all(results)
    apitest = Apitest.query.get(pk)
    apitest.task_id = task_id
    apitest.result = 1 if status else 0
    db.session.commit()
