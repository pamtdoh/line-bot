from . import google_image_crawler

modules = [google_image_crawler]
handlers = filter(lambda module: {'keyword', 'metadata', 'get_response'} <= set(dir(module)), modules)


def handle(keyword, arg):
    for handler in handlers:
        if keyword == handler.keyword:
            return handler.get_response(arg)
    return None
