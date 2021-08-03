FROM python:3.8

LABEL author="wxhou"

WORKDIR /flytest

COPY . .

# ENV FLASK_ENV=development

RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple 

EXPOSE 5000

CMD gunicorn -w 1 -k eventlet -b 0.0.0.0:5000 server:app

