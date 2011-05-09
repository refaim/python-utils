import os
import httplib
import urllib2
import urlparse
import socket

import files
import console

DOWNLOAD_BUFFER_SIZE = 32768 # bytes
DEFAULT_TIMEOUT = 10
DEFAULT_CONNECT_ATTEMPTS_COUNT = 5


def spliturl(url):
    # parse url and get tuple (scheme, netloc, path, params, query, fragment)
    url = urlparse.urlparse(url)
    site, path = url[1], url[2] # netloc, path

    # if 'http://' and 'www' is not present (foo.com/bar/baz, for example)
    # then split full url (parsed to path) to site url and path to html
    # (foo.com and /bar/baz)
    if not site:
        pidx = path.find('/')
        site, path = path[:pidx], path[pidx:]

    return site, path


def getpage(url, maxattempts=DEFAULT_CONNECT_ATTEMPTS_COUNT):
    data = None
    attempts = 0
    while data is None and attempts < maxattempts:
        attempts += 1
        try:
            site, path = spliturl(url)
            connection = httplib.HTTPConnection(site)
            connection.request('GET', path)
            response = connection.getresponse()
            if response.status != httplib.OK:
                continue
            data = response.read()
        except httplib.HTTPException:
            continue
    return data


def handle_network_errors(function, exceptionClass):

    @functools.wraps(function)
    def inner(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except urllib2.HTTPError, ex:
            raise exceptionClass('%d %s' % (ex.code, httplib.responses[ex.code]))
        except urllib2.URLError, ex:
            raise exceptionClass(ex.reason)
        except socket.error, ex:
            format = '[Errno %s] %s' if len(ex.args) == 2 else '%s'
            raise exceptionClass(format % ex.args)

    return inner


def download(src, dst, progress=True, bufsize=DOWNLOAD_BUFFER_SIZE, timeout=DEFAULT_TIMEOUT):
    remote = urllib2.urlopen(src)
    localsize = files.filesize(dst)
    remotesize = int(remote.headers.get('Content-Length') or 0)

    # wrong file
    if remotesize < localsize:
        raise IOError('Local file is larger than the downloaded one')

    # file was not downloaded?
    elif remotesize != localsize:
        request = urllib2.Request(src)
        # try to resume download
        if os.path.exists(dst):
            # set current file size in HTTP 'Range' header for partial content request
            request.headers['Range'] = 'bytes={0}-'.format(localsize)

        remote = urllib2.urlopen(request, timeout=timeout)

        if progress:
            pbar = console.ProgressBar(maxval=remotesize)
            pbar.update(localsize)

        # open destination file
        # and copy bytes chunks
        # from server into local file
        with open(dst, 'ab') as local:
            bytes = remote.read(bufsize)
            while bytes:
                local.write(bytes)
                if progress:
                    pbar.update(len(bytes))
                bytes = remote.read(bufsize)
    return remotesize
