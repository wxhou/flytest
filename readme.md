# WXTEST测试平台

## 启动项目

```shell
flask run
```


## Celery

```shell
celery worker -A server.my_celery -l info -P eventlet
```