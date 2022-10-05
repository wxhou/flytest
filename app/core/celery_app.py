from celery import Celery


celery = Celery('flytest')
celery.config_from_object("app.core.celeryconfig")





