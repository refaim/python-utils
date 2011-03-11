import os
import sys
import hashlib


MD5_READ_BLOCK_SIZE = 2 ** 20 # 1 mb


def filesize(path):
    return (os.path.exists(path) and os.path.isfile(path)
        and os.path.getsize(path) or 0)


def dirsize(path):
    size = 0
    for path, dirs, files in os.walk(path):
        size += sum(os.path.getsize(os.path.join(path, file)) for file in files)
    return size


def md5hash(path):
    with open(path, 'rb') as fobj:
        hobj = hashlib.md5()
        block = fobj.read(MD5_READ_BLOCK_SIZE)
        while block:
            hobj.update(block)
            block = fobj.read(MD5_READ_BLOCK_SIZE)
    return hobj.hexdigest().lower()
