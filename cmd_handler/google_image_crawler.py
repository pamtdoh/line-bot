import os
import pathlib
from cmd_handler.helpers import md5, millis
from linebot.models import ImageSendMessage
from google_images_download import google_images_download
from PIL import Image


keyword = 'heh'
metadata = {}
def get_response(arg):
    return get_image_pairs_urls(arg, 5) if arg else None


file_root_path = pathlib.Path(os.getenv('FILE_ROOT_PATH', None))
image_path = file_root_path / 'images'
server_root = os.getenv('SERVER_ROOT', None)

original_size = 1536
preview_size = 512

crawler = google_images_download.googleimagesdownload()


def get_download_paths(search_key, start, limit=5):
    search_key = search_key.replace(',', ' ')

    args = {
        'keywords': search_key,
        'offset': start + 1,
        'limit': start + limit,
        'no_numbering': True,
        'silent_mode': True
    }

    return crawler.download(args)[0][search_key]


def generate_image_pair(download_path, dirname, filename):
    try:
        image = Image.open(download_path)
        ext = 'jpg' if image.format == 'JPEG' else 'png'
        width, height = image.size

        def get_image_ratio(size):
            return 1 if width < size and height < size else size / max(width, height)

        def save_image(filename, size):
            ratio = get_image_ratio(size)
            path = image_path / dirname / f'{filename}.{ext}'
            new_image = image.resize((int(width * ratio), int(height * ratio)), Image.ANTIALIAS)

            os.makedirs(os.path.dirname(path), exist_ok=True)
            new_image.save(path)

            return path

        original_path = save_image(filename, original_size)
        preview_path = save_image(f'{filename}p', preview_size)

        return original_path, preview_path
    except OSError:
        return


def get_image_pairs(search_key, start, n):
    dirname = md5(search_key)
    prefix = str(millis())

    download_paths = []
    limit = 5

    path_pairs = []
    while len(path_pairs) < n:
        if not download_paths:
            # the list is reversed so the order is preserved when popped
            download_paths = get_download_paths(search_key, start, limit)
            download_paths.reverse()
            start += limit

        download_path = download_paths.pop()
        if os.path.exists(download_path):
            pair = generate_image_pair(download_path, dirname, f'{prefix}_{len(path_pairs)}')
            if pair:
                path_pairs.append(pair)

    return path_pairs


def get_image_pairs_urls(search_key, n):
    def file_path_to_url(path):
        return server_root + '/' + '/'.join(path.relative_to(file_root_path).parts)

    return [ImageSendMessage(file_path_to_url(original_path), file_path_to_url(preview_path))
            for original_path, preview_path
            in get_image_pairs(search_key, 0, n)]
