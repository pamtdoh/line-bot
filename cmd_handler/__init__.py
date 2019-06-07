from .dfrotz import Dfrotz
from .google_image_crawler import GoogleImageCrawler

handlers = [GoogleImageCrawler, Dfrotz]


def handle(message_event):
    for handler in handlers:
        if handler.matcher(message_event):
            return handler.response(message_event)
    return None
