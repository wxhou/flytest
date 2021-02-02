broker_url = 'redis://127.0.0.1:6379'
result_backend = 'redis://127.0.0.1:6379'


# 启动celery的shell命令
# celery worker -A flytest -l info -P eventlet