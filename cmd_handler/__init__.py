from .google_image_crawler import GoogleImageCrawler
from .helpers import get_keyword

handlers = [GoogleImageCrawler]


def handle(message_event):
    keyword = get_keyword(message_event)
    for handler in handlers:
        if keyword in handler.match_keywords:
            return handler.response(message_event)
    return None
