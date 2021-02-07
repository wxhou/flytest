from flytest.extensions import db
from flytest.models import Apistep, Apitest, Report, Bug
from flytest.request import HttpRequest
from flytest.utils import generate_url
from flytest import celery_app
from flask import current_app

celery = celery_app(current_app)


@celery.task
def apistep_job(pk):
    apistep = Apistep.query.get(pk)
    task_id = apistep_job.request.id
    HttpRequest().http_request(apistep, task_id)
    if Apistep.query.filter_by(apitest_id=apistep.apitest_id).count() == 1:
        apitest = Apitest.query.get(apistep.apitest_id)
        apitest.task_id = task_id
        apitest.results = apistep.status
        db.session.commit()


@celery.task
def apitest_job(pk):
    task_id = apitest_job.request.id
    apitest = Apitest.query.get_or_404(pk)
    apisteps = Apistep.query.filter_by(apitest=apitest, is_deleted=False)
    for step in apisteps:
        HttpRequest().http_request(step, task_id)
    current_app.logger.info("测试完成！")
    apisteps = Apistep.query.filter_by(apitest_id=pk)
    results = []
    for i in apisteps:
        report = Report(task_id=i.apitest.task_id, name=apitest.name,
                        result=i.results, status=i.status, is_deleted=False)
        db.session.add(report)
        report.apistep = i
        if i.status == 0:
            bug = Bug(task_id=task_id, casename=i.apitest.name, stepname=i.name,
                      request="""
                        请求方法：{}
                        请求地址：{}
                        请求内容：{}
                        """.format(i.method, generate_url(i.apiurl.url, i.route), i.request_data),
                      detail="""
                    预期结果：{}
                    实际结果：{}
                    """.format(i.expected_result, i.results),
                      status=i.status,
                      is_deleted=False)
            db.session.add(bug)
        results.append(i.status)
    status = all(results)
    apitest.task_id = task_id
    apitest.result = 1 if status else 0
    db.session.commit()
