# from .dfrotz import Dfrotz
from .google_image_crawler import NewSearch, NextSearch

handlers = [NewSearch, NextSearch]


def handle(event):
    for handler in handlers:
        instance = handler(event)
        if instance.match():
            return instance.response()
    return None
