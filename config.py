import os


class Config:
    APPLICATION_ROOT = os.getenv('FILE_ROOT_DIR')
    SERVER_URL = os.getenv('SERVER_URL')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(APPLICATION_ROOT, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
    CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')

    image_dir = os.path.join(APPLICATION_ROOT, 'images')
    original_size = 1536
    preview_size = 512
