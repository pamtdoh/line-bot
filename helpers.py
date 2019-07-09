from datetime import datetime
import hashlib
import time


def source_type(event):
    return event.source.type


def timestamp(event):
    return datetime.fromtimestamp(event.timestamp / 1000)


def source_user_id(event):
    return event.source.user_id


def source_group_id(event):
    return event.source.group_id if event.source.type == 'group' else \
           event.source.room_id if event.source.type == 'room' else \
           event.source.user_id


def message_text(event):
    return event.message.text


def md5(string):
    return hashlib.md5(string.encode()).hexdigest()


def millis():
    return int(time.time() * 1000)
