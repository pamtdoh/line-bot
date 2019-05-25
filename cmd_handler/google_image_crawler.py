import os
import pathlib
import time
from linebot.models import ImageSendMessage
from google_images_download import google_images_download
from PIL import Image


keyword = 'heh'
metadata = {}
def get_response(arg):
    return get_image_pairs_urls(get_paths(arg)) if arg else None


file_root_path = pathlib.Path(os.getenv('FILE_ROOT_PATH', None))
image_path = file_root_path / 'images'
server_root = os.getenv('SERVER_ROOT', None)

original_size = 1024
preview_size = 240

crawler = google_images_download.googleimagesdownload()


def get_paths(search_key):
    search_key = search_key.replace(',', ' ')

    args = {
        'keywords': search_key,
        'limit': 5,
        'no_numbering': True,
        # 'thumbnail_only': True
        # 'no_download': True
    }

    return crawler.download(args)[0][search_key]


def generate_image_pair(path, dirname, filename):
    try:
        image = Image.open(path)
        width, height = image.size

        def get_image_ratio(size):
            return 1 if width < size and height < size else size / max(width, height)

        def save_image(size, save_path):
            ratio = get_image_ratio(size)
            new_path = save_path / dirname / filename
            new_image = image.resize((int(width * ratio), int(height * ratio)), Image.ANTIALIAS)

            os.makedirs(os.path.dirname(new_path), exist_ok=True)
            new_image.save(new_path, image.format)

            return new_path

        original_path = save_image(original_size, image_path / 'original')
        preview_path = save_image(preview_size, image_path / 'preview')

        return original_path, preview_path
    except OSError:
        return


def file_path_to_url(path):
    return server_root + '/' + '/'.join(path.relative_to(file_root_path).parts)


def get_image_pairs_urls(paths):
    dirname = str(int(time.time() * 1000))
    image_pairs_paths = [generate_image_pair(path, dirname, str(index))
                         for index, path in enumerate(paths)
                         if os.path.exists(path) and path]

    return [ImageSendMessage(file_path_to_url(original_path), file_path_to_url(preview_path))
            for original_path, preview_path in image_pairs_paths]
