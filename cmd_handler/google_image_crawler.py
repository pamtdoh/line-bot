import os
from pathlib import Path
from app import db
from config import Config
from .helpers import (
    get_timestamp, get_source_type, get_user_id, get_group_id,
    get_keyword, get_search_key,
    md5
)
from linebot.models import ImageSendMessage
from google_images_download import google_images_download
from .models import Search
from PIL import Image


class GoogleImageCrawler:
    metadata = {}
    match_keywords = ['heh', 'hehh']
    @staticmethod
    def response(event):
        keyword = get_keyword(event)
        if keyword == 'heh':
            return GoogleImageCrawler.new_search(event).get_response()
        else:
            return GoogleImageCrawler.latest_search(event).get_response()

    def __init__(self, event):
        self.crawler = google_images_download.googleimagesdownload()

        self.event = event
        self.search = None

    @staticmethod
    def new_search(event):
        h = GoogleImageCrawler(event)
        h.search = Search(
            timestamp=get_timestamp(h.event),
            type=get_source_type(h.event),
            userId=get_user_id(h.event),
            groupId=get_group_id(h.event),
            searchKey=get_search_key(h.event)
        )
        db.session.add(h.search)
        db.session.commit()
        return h

    @staticmethod
    def latest_search(event):
        h = GoogleImageCrawler(event)
        h.search = Search.query.filter(
            Search.userId == get_user_id(event),
            Search.groupId == get_group_id(event)
        ).order_by(Search.timestamp.desc()).first()
        return h

    def get_response(self):
        if self.search:
            response = self.get_image_pairs_urls(5) if self.search.searchKey else None
            db.session.commit()
            return response

    def get_image_pairs(self, n):
        dirname = md5(self.search.searchKey)

        limit = 5
        download_paths = []

        path_pairs = []
        while len(path_pairs) < n:
            if not download_paths:
                # the list is reversed so the order is preserved when popped
                download_paths = self.get_download_paths(limit)
                download_paths.reverse()
                self.search.start += limit

            download_path = download_paths.pop()
            if os.path.exists(download_path):
                pair = self.generate_image_pair(download_path, dirname, str(self.search.count))
                if pair:
                    path_pairs.append(pair)
                    self.search.count += 1
        self.search.start -= len(download_paths)

        return path_pairs

    def get_image_pairs_urls(self, n):
        def file_path_to_url(path):
            return Config.SERVER_URL + '/' + '/'.join(path.relative_to(Config.APPLICATION_ROOT).parts)

        return [ImageSendMessage(file_path_to_url(original_path), file_path_to_url(preview_path))
                for original_path, preview_path
                in self.get_image_pairs(n)]

    def get_download_paths(self, limit=5):
        search_key = self.search.searchKey.replace(',', ' ')

        args = {
            'keywords': search_key,
            'offset': self.search.start + 1,
            'limit': self.search.start + limit,
            'no_numbering': True,
            'silent_mode': True
        }

        return self.crawler.download(args)[0][search_key]

    @staticmethod
    def generate_image_pair(download_path, dirname, filename):
        try:
            image = Image.open(download_path)
            ext = 'jpg' if image.format == 'JPEG' else 'png'
            width, height = image.size

            def get_image_ratio(size):
                return 1 if width < size and height < size else size / max(width, height)

            def save_image(filename, size):
                ratio = get_image_ratio(size)
                path = Path(Config.image_dir) / dirname / f'{filename}.{ext}'
                new_image = image.resize((int(width * ratio), int(height * ratio)), Image.ANTIALIAS)

                os.makedirs(os.path.dirname(path), exist_ok=True)
                new_image.save(path)

                return path

            original_path = save_image(filename, Config.original_size)
            preview_path = save_image(f'{filename}p', Config.preview_size)

            return original_path, preview_path
        except OSError:
            return
