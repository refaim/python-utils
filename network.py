import os
import urllib2

import files
import console

DOWNLOAD_BUFFER_SIZE = 32768 # bytes


def download(src, dst, progress=True, bufsize=DOWNLOAD_BUFFER_SIZE):
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

        remote = urllib2.urlopen(request)

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
