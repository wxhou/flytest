from settings import *


DEBUG = True
SECRET_KEY = os.getenv('SECRET_KEY', "ahJ#5UoEg9x1T&@n")

PER_PAGE_SIZE = 10

DB_SERVER = '127.0.0.1'
SQLALCHEMY_ECHO = True
SQLALCHEMY_RECORD_QUERIES = True
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = "mysql://root:root1234@{}:3306/flytest".format(DB_SERVER)

# email
MAIL_SERVER = os.getenv('MAIL_SERVER')
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
MAIL_DEFAULT_SENDER = ('wxtest', MAIL_USERNAME)

# debugtool
DEBUG_TB_PROFILER_ENABLED = False
DEBUG_TB_TEMPLATE_EDITOR_ENABLED = False
DEBUG_TB_INTERCEPT_REDIRECTS = False

# celery
CELERY_BROKER_URL = 'redis://{}:6379/1'.format(DB_SERVER)
CELERY_RESULT_BACKEND = 'redis://{}:6379/2'.format(DB_SERVER)
# cache
CACHE_CONFIG = {
    'CACHE_TYPE': "redis",  # Flask-Caching related configs
    'CACHE_REDIS_HOST': DB_SERVER,
    'CACHE_REDIS_PORT': 6379,
    "CACHE_DEFAULT_TIMEOUT": 600
}

# crontab
SCHEDULER_API_ENABLED = True

SCHEDULER_JOBSTORES = {
    'default': SQLAlchemyJobStore(url=SQLALCHEMY_DATABASE_URI)
}

SCHEDULER_EXECUTORS = {
    'default': {'type': 'threadpool', 'max_workers': 20}
}

SCHEDULER_JOB_DEFAULTS = {
    'coalesce': False,
    'max_instances': 3
}

