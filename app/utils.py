import os
import json
import uuid
import time
import string
import random
from itertools import product
from urllib.parse import urljoin
from flask import jsonify, current_app
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from settings import BASE_DIR


def generate_url(url, route):
    """
    generate url
    :param url:
    :param route:
    :return:
    """
    current_app.logger.info("请求服务器：{}".format(url))
    current_app.logger.info("请求路径：`{}`".format(route))
    if not route:
        return url.strip()
    return urljoin(url.strip(), route.strip())


def header_to_dict(raw_str):
    """header to dict
    :type raw_str: str
    """
    if '\\n' in raw_str:
        raw_str = raw_str.split('\\n')
    else:
        raw_str = raw_str.split('\n')
    res = [[k.strip() for k in i.split(": ")] for i in raw_str]
    return dict(res)


def params2dict(raw_str):
    """get params to dict
    """
    if isinstance(raw_str, dict):
        return raw_str
    new_dict = dict(i.split('=') for i in raw_str.split('&'))
    return new_dict


def is_json_str(string):
    """str is json str
    """
    if isinstance(string, str):
        try:
            data = json.loads(string)
            return data
        except ValueError:
            return False
    return False


def make_dir(dir):
    if '.' in dir:
        dir = os.path.dirname(dir)
    if os.path.exists(dir):
        return dir
    else:
        os.makedirs(dir)
        return dir


def response_error(code, msg="None"):
    return jsonify({'errcode': code, 'errmsg': msg})


def response_success(**kwargs):
    res = {'errcode': 0, 'errmsg': '任务正在运行！'}
    for k, v in kwargs.items():
        res[k] = v
    return jsonify(res)


def uid_name():
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, str(time.time())))


def random_code(length=4):
    """随机验证码"""
    return "".join(random.sample(string.ascii_letters+string.digits, length))


def random_color(s=1, e=255):
    """随机颜色"""
    return (random.randint(s, e), random.randint(s, e), random.randint(s, e))


def get_captcha(length=4, width=120, height=40):
    """生成验证码"""
    font_file = os.path.join(BASE_DIR, 'font', 'arial.ttf')
    image = Image.new('RGB', (width, height), (255, 255, 255))  # 创建Image对象
    font = ImageFont.truetype(font_file, 32)    # 创建Font对象
    draw = ImageDraw.Draw(image)    # 创建Draw对象
    for x, y in product(range(width), range(height)):
        draw.point((x, y), fill=random_color(128, 255))  # 随机颜色填充每个像素
    code = random_code(length)    # 验证码
    for t in range(length):
        draw.text((30*t+5, 1), code[t], font=font,
                  fill=random_color(0, 127))    # 写到图片上
    image = image.filter(ImageFilter.BoxBlur(1))    # 模糊图像
    # image.save(f"{code}.png", )  # 保存图片
    # image.show()
    return code, image


if __name__ == '__main__':
    print(get_captcha())
