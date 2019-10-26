# from .dfrotz import Dfrotz
from .google_image_crawler import NewSearch, NextSearch
from .dfrotz import ListRoms, DfrotzNew, DfrotzInput

handlers = [DfrotzInput, NewSearch, NextSearch, DfrotzNew, ListRoms]


def handle(event):
    for handler in handlers:
        instance = handler(event)
        if instance.match():
            return instance.response()
    return None
