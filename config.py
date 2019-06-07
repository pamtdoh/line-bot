import os


class Config:
    SERVER_URL = os.getenv('SERVER_URL')
    FILE_ROOT_DIR = os.getenv('FILE_ROOT_DIR')
    APP_ROOT = os.getenv('APP_ROOT')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(APP_ROOT, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
    CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
