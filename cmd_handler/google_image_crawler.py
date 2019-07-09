import os
from pathlib import Path
from app import db
from config import Config
from helpers import message_text, md5
from linebot.models import ImageSendMessage
from google_images_download import google_images_download
from models import Search
from PIL import Image


image_dir = os.path.join(Config.FILE_ROOT_DIR, 'images')
original_size = 1536
preview_size = 512


class NewSearch:
    def __init__(self, event):
        self.event = event

        text = message_text(event)
        self.keyword = keyword(text)
        self.search_key = rest(text)

    def match(self):
        return self.keyword == 'heh' and self.search_key

    def response(self):
        search = Search(self.event, self.search_key)
        db.session.add(search)
        db.session.commit()

        response = get_response_and_update(search, 5)
        return response


class NextSearch:
    def __init__(self, event):
        self.event = event
        self.keyword = keyword(message_text(event))
        self.last_search = Search.last(event)

    def match(self):
        return self.keyword == 'hehh' and self.last_search

    def response(self):
        response = get_response_and_update(self.last_search, 5)
        return response


metadata = {}

crawler = google_images_download.googleimagesdownload()


def get_response_and_update(search, n):
    def file_path_to_url(path):
        return Config.SERVER_URL + '/' + '/'.join(path.relative_to(Config.FILE_ROOT_DIR).parts)

    return [ImageSendMessage(file_path_to_url(original_path), file_path_to_url(preview_path))
            for original_path, preview_path
            in get_image_and_update(search, n)]


def get_image_and_update(search, n):
    dirname = md5(search.searchKey)

    limit = 5
    download_paths = []

    path_pairs = []
    while len(path_pairs) < n:
        if not download_paths:
            # the list is reversed so the order is preserved when popped
            download_paths = fetch_download_paths(search.searchKey, search.start, limit)
            download_paths.reverse()
            search.start += limit

        download_path = download_paths.pop()
        if os.path.exists(download_path):
            pair = generate_image_pair(download_path, dirname, str(search.count))
            if pair:
                path_pairs.append(pair)
                search.count += 1
    search.start -= len(download_paths)

    db.session.commit()
    return path_pairs


def fetch_download_paths(search_key, start, limit=5):
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
            path = Path(image_dir) / dirname / f'{filename}.{ext}'
            new_image = image.resize((int(width * ratio), int(height * ratio)), Image.ANTIALIAS)

            os.makedirs(os.path.dirname(path), exist_ok=True)
            new_image.save(path)

            return path

        original_path = save_image(filename, original_size)
        preview_path = save_image(f'{filename}p', preview_size)

        return original_path, preview_path
    except OSError:
        return


def keyword(text):
    return text.split()[0]


def rest(text):
    return text[len(keyword(text)):].lstrip()
