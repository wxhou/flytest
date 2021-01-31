from flytest import celery


@celery.task()
def add():
    pass
