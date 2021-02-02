broker_url = 'redis://127.0.0.1:6379/1'
result_backend = 'redis://127.0.0.1:6379/2'


# 启动celery的shell命令
# celery worker -A flytest.tasks -l info -P eventlet