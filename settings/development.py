from settings import *


DEBUG = True
SECRET_KEY = os.getenv('SECRET_KEY', "ahJ#5UoEg9x1T&@n")

PER_PAGE_SIZE = 10

DB_SERVER = os.getenv("DB_SERVER", "127.0.0.1")
SQLALCHEMY_ECHO = True
SQLALCHEMY_RECORD_QUERIES = True
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = "mysql://root:root1234@%s:3306/flytest" % DB_SERVER

# email
MAIL_SERVER = os.getenv('MAIL_SERVER')
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
MAIL_DEFAULT_SENDER = ('wxtest', MAIL_USERNAME)

# cache
CACHE_CONFIG = {
    'CACHE_TYPE': "redis",  # Flask-Caching related configs
    'CACHE_REDIS_HOST': DB_SERVER,
    'CACHE_REDIS_PORT': 6379,
    "CACHE_DEFAULT_TIMEOUT": 600
}

# crontab-config
SCHEDULER_API_ENABLED = True
SCHEDULER_TIMEZONE = 'Asia/Shanghai'
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
