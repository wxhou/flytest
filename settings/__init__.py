import os
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AVATARS_SAVE_PATH = os.path.join(BASE_DIR, 'media', 'avatars')
IMAGES_PATH = os.path.join(BASE_DIR, 'media', 'images')
VIDEOS_PATH = os.path.join(BASE_DIR, 'media', 'videos')
AUDIOS_PATH = os.path.join(BASE_DIR, 'media', 'audios')
FLASK_LOGGER_FILE = os.path.join(BASE_DIR, 'logs', 'server.log')
