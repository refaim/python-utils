from __future__ import print_function

import sys


class ProgressBar(object):
    def __init__(self, maxval, fout=sys.stderr, width=None, displaysize=False, only_r=True):
        self.maxval = maxval
        self.fout = fout
        self.width = width
        self.displaysize = displaysize
        self.curval = 0
        self.only_r = only_r
        self.terminal_width = getTerminalWidth()
        if self.width is None:
            # '[===...===] X%\n'
            # length of _getbarstr()
            self.width = (self.terminal_width - len('[]') - len(' 100%\n')) / 2
            if self.displaysize:
                # subtract max length of size string
                self.width -= len(' [1023.99 GiB / 9999.99 TiB]')

    def start(self):
        self.set(0)

    def update(self, value):
        assert (self.curval + value) <= self.maxval
        self.curval += value
        self._write()

    def set(self, value):
        assert value <= self.maxval
        self.curval = value
        self._write()

    def finish(self):
        if not self.completed:
            self.set(self.maxval)

    def percentage(self):
        return int(self.curval / float(self.maxval) * 100.0)

    @property
    def completed(self):
        return self.curval == self.maxval

    def clear(self):
        '(Temporarily) clear progress bar off screen, e.g. to write log line.'
        self.fout.write(' ' * (self.terminal_width - len('\r')) + '\r')
        self.fout.flush()

    def _getbarstr(self):
        result = '=' * int(self.percentage() * (self.width / 100.0))
        if not self.completed:
            result += '>'
        return result.ljust(self.width)

    def _getsizestr(self):
        return '[%s / %s]' % tuple(map(bytes_to_human, (self.curval, self.maxval)))

    def _write(self):
        line = '[%s] %s%%' % (self._getbarstr(), self.percentage())
        if self.displaysize:
            line = '%s %s' % (line, self._getsizestr())

        ending = '\n' if self.completed and not self.only_r else '\r'
        line = line.ljust(self.terminal_width - len(ending)) + ending

        # encoding is None if output redirected to a file
        if self.fout.encoding:
            line = line.encode(self.fout.encoding)

        self.fout.write(line)
        self.fout.flush()


def bytes_to_human(bytes):
    bounds = {
        1024 ** 4: 'TiB',
        1024 ** 3: 'GiB',
        1024 ** 2: 'MiB',
        1024:      'KiB',
        0:         'b'
    }

    bytes = float(bytes)
    for bound in sorted(bounds.keys(), reverse=True):
        if bytes >= bound:
            if bound != 0:
                bytes = bytes / bound
            return '{0:.2f} {1}'.format(bytes, bounds[bound])


def getTerminalSize():
    if 'win32' in sys.platform:
        return _win32_get_terminal_size()
    else:
        return _unix_get_terminal_size()


def getTerminalWidth():
    return getTerminalSize()[0]


def getTerminalHeight():
    return getTerminalSize()[1]


def writeline(value, ljust=True, end='\r'):
    if not isinstance(value, basestring):
        value = '{0}'.format(value)
    print(value.ljust(getTerminalWidth()), end=end)


def _win32_get_terminal_size():
    # http://code.activestate.com/recipes/440694-determine-size-of-console-window-on-windows/
    from ctypes import windll, create_string_buffer
    # stdin handle is -10
    # stdout handle is -11
    # stderr handle is -12
    h = windll.kernel32.GetStdHandle(-12)
    csbi = create_string_buffer(22)
    res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
    if res:
        import struct
        (bufx, bufy, curx, cury, wattr,
         left, top, right, bottom, maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
        sizex = right - left + 1
        sizey = bottom - top + 1
    else:
        sizex, sizey = 80, 25 # can't determine actual size - return default values
    return sizex, sizey


def _unix_get_terminal_size():

    def ioctl_GWINSZ(fd):
        try:
            import fcntl, termios, struct, os
            cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ,
        '1234'))
        except:
            return None
        return cr

    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        try:
            cr = (env['LINES'], env['COLUMNS'])
        except:
            cr = (25, 80)
    return int(cr[1]), int(cr[0])
