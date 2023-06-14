import os
from celery import Celery
from app import celeryconfig
from app import create_app


BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def make_celery(app_name):
    _celery = Celery(app_name,
                    broker=celeryconfig.broker_url,
                    backend=celeryconfig.result_backend)
    _celery.config_from_object(celeryconfig)
    _celery.autodiscover_tasks(['app'])
    return _celery


celery = make_celery(__name__)
app = create_app(celery=celery)
if __name__ == "__main__":
    app.run(debug=True)