# FlyTest测试平台

### 初始化数据库

```shell
flask db init
```
```shell
flask db migrate
```
```shell
flask db upgrade
```

### 启动项目

```shell
flask run
```


## 启动Celery

```shell
celery -A app.core.celery_app.celery worker -l info -P eventlet
```

### 版本更新记录

V1.1

    ——更新celery与项目的组织结构方式


V1.0

    ——flask前后端不分离

1. 项目管理
2. 环境管理
3. 测试管理——requests接口测试
4. 任务管理——celery异步执行测试
5. 定时任务——APScheduler定时任务
6. 缺陷管理
7. 报告管理——结果趋势
