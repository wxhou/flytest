import os
from flytest import BASE_DIR


DEBUG = True
SECRET_KEY = os.getenv('SECRET_KEY', "ahJ#5UoEg9x1T&@n")

PER_PAGE_SIZE = 10

DB_SERVER = os.getenv("DB_SERVER", "127.0.0.1")
SQLALCHEMY_ECHO = True
SQLALCHEMY_RECORD_QUERIES = True
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = "mysql://root:root1234@%s:3306/flytest" % DB_SERVER

# email
MAIL_SERVER = os.getenv("MAIL_SERVER", 'smtp.126.com')
MAIL_PORT = os.getenv("MAIL_PORT", 25)
MAIL_USERNAME = os.getenv("MAIL_USERNAME", 'twxhou@126.com')
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", 'GQWJDUKVWNOJLPOH')
MAIL_DEFAULT_SENDER = (os.getenv("MAIL_DEFAULT_SENDER", 'WXTEST Admin'), MAIL_USERNAME)

# cache
CACHE_CONFIG = {
    'CACHE_TYPE': "redis",  # Flask-Caching related configs
    'CACHE_REDIS_HOST': DB_SERVER,
    'CACHE_REDIS_PORT': 6379,
    "CACHE_DEFAULT_TIMEOUT": 600
}

AVATARS_SAVE_PATH = os.path.join(BASE_DIR, 'media', 'avatars')
IMAGES_PATH = os.path.join(BASE_DIR, 'media', 'images')
VIDEOS_PATH = os.path.join(BASE_DIR, 'media', 'videos')
AUDIOS_PATH = os.path.join(BASE_DIR, 'media', 'audios')
FLASK_LOGGER_FILE = os.path.join(BASE_DIR, 'logs', 'server.log')
CAPTCHA_FONT_FILE = os.path.join(BASE_DIR, 'media', 'fonts', 'arial.ttf')


# crontab-config
SCHEDULER_API_ENABLED = True
SCHEDULER_TIMEZONE = 'Asia/Shanghai'

SCHEDULER_EXECUTORS = {
    'default': {'type': 'threadpool', 'max_workers': 20}
}

SCHEDULER_JOB_DEFAULTS = {
    'coalesce': False,
    'max_instances': 3
}
