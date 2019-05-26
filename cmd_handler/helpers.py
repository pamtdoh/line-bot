import hashlib
import time


def md5(string):
    return hashlib.md5(string.encode()).hexdigest()


def millis():
    return int(time.time() * 1000)