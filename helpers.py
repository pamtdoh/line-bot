from datetime import datetime
import hashlib
import os
import time


def get_source_type(event):
    return event.source.type


def get_timestamp(event):
    return datetime.fromtimestamp(event.timestamp / 1000)


def get_source_user_id(event):
    return event.source.user_id


def get_source_group_id(event):
    return event.source.group_id if event.source.type == 'group' else \
           event.source.room_id if event.source.type == 'room' else \
           event.source.user_id

def get_text(message_event):
    return message_event.message.text


def get_keyword(message_event):
    return get_text(message_event).split()[0]


def get_search_key(event):
    return get_text(event)[len(get_keyword(event)):].lstrip()


def md5(string):
    return hashlib.md5(string.encode()).hexdigest()


def millis():
    return int(time.time() * 1000)
