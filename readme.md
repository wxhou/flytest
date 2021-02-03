flask db init

flask db migrate -m"版本名(注释)"

flask db upgrade 然后观察表结构

```python
# 启动celery的shell命令
# celery worker -A flytest.tasks -l info -P eventlet
```