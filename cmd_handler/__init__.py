from . import google_image_crawler

modules = [google_image_crawler]
handlers = [module for module in modules
            if {'keyword', 'metadata', 'get_response'} <= set(dir(module))]


def handle(keyword, arg):
    for handler in handlers:
        if keyword == handler.keyword:
            return handler.get_response(arg)
    return None
