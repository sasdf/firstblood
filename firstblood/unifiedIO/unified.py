import io
import os
import functools as fn
from math import inf


# TODO: regex readuntil, timeout, abstract


def _UnsupportedOperation(*args, **kwargs):
    raise io.UnsupportedOperation()


def _chainWrapper(func, self=None, name=None):
    @fn.wraps(func)
    def inner(*args, **kwargs):
        func(*args, **kwargs)
        return self if self is not None else args[0]
    if name is not None:
        inner.__qualname__ = name
        inner.__name__ = name.rsplit('.', 1)[-1]
    return inner


class Unified(object):
    def __init__(self, file):
        # Variables - private
        self._buffer = ''
        self._empty = ''
        self._linesep = os.linesep
        self._BUFFER_SIZE = io.DEFAULT_BUFFER_SIZE
        if 'b' in file.mode:
            self._buffer = self._buffer.encode('utf8')
            self._empty = self._empty.encode('utf8')
            self._linesep = self._linesep.encode('utf8')


        # Function pointers
        self._read = file.read
        self._readable = file.readable
        self._readline = file.readline
        self._write = file.write
        self._writable = file.writable
        self._writelines = file.writelines
        self._seek = file.seek
        self._seekable = file.seekable
        self._tell = file.tell
        self._flush = file.flush
        self._close = file.close
        self._enter = file.__enter__
        self._exit = file.__exit__

        if hasattr(file, 'read1'):
            self._read1 = file.read1

        # Variables - public
        self.raw = file
        self.closed = file.closed

        # Bindings
        self.detach = _UnsupportedOperation
        self.fileno = file.fileno
        self.isatty = file.isatty
        self.mode = file.mode
        self.name = file.name
        self.readinto = _UnsupportedOperation
        self.readinto1 = _UnsupportedOperation
        self.truncate = file.truncate
        self.__iter__ = _UnsupportedOperation
        self.__next__ = _UnsupportedOperation

    # Virtuals Methods
    _read       = _UnsupportedOperation
    _readable   = _UnsupportedOperation
    _write      = _UnsupportedOperation
    _writeable  = _UnsupportedOperation
    _seek       = _UnsupportedOperation
    _seekable   = _UnsupportedOperation
    _tell       = _UnsupportedOperation
    _close      = _UnsupportedOperation
    _flush      = _UnsupportedOperation

    def _readline(self, size=-1):
        return self.readuntil(self._linesep, size, keep=True, drop=True)

    def _read1(self, size=-1):
        if size < 0:
            size = self._BUFFER_SIZE
        return self._read(size)

    def _writelines(self, lines):
        b = self._empty.join(lines)
        self._write(b)
        return b

    def _enter(self):
        return self

    def _exit(self, *exc_details):
        if not self.closed: # Recursive guard
            self.close()

    # Private Methods

    def _get(self, pos=-1, needle=0, keep=False, drop=True):
        if pos < 0 or pos is inf:
            res, self._buffer = self._buffer, self._empty
            return res
        if keep:
            left, right = pos + needle, pos + needle
        elif drop:
            left, right = pos, pos + needle
        else:
            left, right = pos, pos
        res, self._buffer = self._buffer[:left], self._buffer[right:]
        return res

    # Public Methods

    def close(self, *args, **kwargs):
        self.closed = True # Recursive guard
        self._close(*args, **kwargs)

    def readlines(self, hint=-1, keep=False):
        if hint == 0:
            return []

        if hint > 0 and len(self._buffer) >= hint:
            res = self._get(hint)
            res = res.splitlines(keep)
        else:
            res = self._get()
            if hint > 0:
                hint -= len(res)
            res2 = self._read(hint).splitlines(keep)
            if len(res2):
                res += res2.pop(0)
            res = res.splitlines(keep)
            res.extend(res2)
        return res

    def lines(self, hint=-1, keep=False):
        if isinstance(hint, type(self._empty)):
            return self.writeline(hint)
        return self.readline(hint, keep)

    def readline(self, size=-1, keep=False):
        if size == 0:
            return self._empty

        if len(self._buffer):
            s = self.peek(size, imm=True)
            s, t = s.splitlines(True)[0], s.splitlines(False)[0]
            if len(s) > len(t):
                return self._get(len(t), len(s) - len(t), keep, True)

        if size > 0 and len(self._buffer) >= size:
            return self._get(size)

        res = self._get()
        if size > 0:
            size -= len(res)
        res += self._readline(size)
        if not keep and len(res):
            res = res.splitlines(False)[0]
        return res
    nextline = _chainWrapper(readline, name='Unified.nextline')

    def line(self, size=-1, keep=False):
        if isinstance(size, type(self._empty)):
            return self.writeline(size)
        return self.readline(size, keep)

    def tell(self):
        return self._tell() - len(self._buffer)

    def seek(self, *args, **kwargs):
        if self._seekable():
            self._buffer = self._empty
        self._seek(*args, **kwargs)
        return self

    def read1(self, size=-1):
        if size == 0:
            return self._empty
        if len(self._buffer):
            return self._get(size)
        return self._read1(size)

    def read(self, size=-1):
        if size == 0:
            return self._empty
        if size > 0 and len(self._buffer) >= size:
            return self._get(size)
        res = self._get()
        res += self._read(size - len(res))
        return res

    def peek(self, size=-1, imm=False):
        if size == 0:
            return self._empty
        if not len(self._buffer) and not imm:
            self.buffer += self.read1(size)
        if size is inf or size < 0:
            return self._buffer
        return self._buffer[:size]

    def readuntil(self, expected, size=-1, keep=False, drop=True):
        explen = len(expected)
        if not explen:
            raise ValueError('`expected` should not be empty string')
        chunkSZ = max(explen, self._BUFFER_SIZE)

        if size < 0:
            size = inf

        res = self.peek(size, imm=True)
        pos = res.find(expected)
        if pos != -1:
            return self._get(pos, explen, keep, drop)

        if len(self._buffer) >= size:
            return self._get(size)

        size -= len(self._buffer)
        while size:
            sz = min(size, chunkSZ)
            s = self._read(sz)
            if not len(s):
                break
            off = max(0, len(self._buffer) - explen)
            size -= len(s)
            self._buffer += s
            pos = self._buffer[off:].find(expected)
            if pos != -1:
                return self._get(off + pos, explen, keep, drop)
        return self._get()
    until = readuntil
    before = _chainWrapper(
        fn.partial(readuntil, keep=False, drop=False),
        name='Unified.before')
    after = _chainWrapper(
        fn.partial(readuntil, keep=False, drop=True),
        name='Unified.after')

    def writeline(self, b):
        self._write(b + self._linesep)
        return self

    def __repr__(self):
        res = repr(self.raw)
        if res.startswith('<'):
            return f'<Unified {res[1:]}'
        else:
            return f'<Unified {res}>'

    def __enter__(self, *args, **kwargs):
        self._enter(*args, **kwargs)
        return self

def _createPlaceholder(module, funcname, attr=None, chainable=False):
    if hasattr(module, funcname):
        return
    if attr is None:
        attr = funcname
    def inner(self, *args, **kwargs):
        res = getattr(self, attr)(*args, **kwargs)
        return self if chainable else res
    inner.__name__ = funcname
    inner.__qualname__ = f'{module.__name__}.{funcname}'
    setattr(module, funcname, inner)


_createPlaceholder(Unified, 'read',       '_read',       False)
_createPlaceholder(Unified, 'read1',      '_read1',      False)
_createPlaceholder(Unified, 'readable',   '_readable',   False)
_createPlaceholder(Unified, 'readline',   '_readline',   False)
_createPlaceholder(Unified, 'readlines',  '_readlines',  False)
_createPlaceholder(Unified, 'write',      '_write',      True )
_createPlaceholder(Unified, 'writable',   '_writable',   False)
_createPlaceholder(Unified, 'writeline',  '_writeline',  True )
_createPlaceholder(Unified, 'writelines', '_writelines', True )
_createPlaceholder(Unified, 'seek',       '_seek',       True )
_createPlaceholder(Unified, 'seekable',   '_seekable',   False)
_createPlaceholder(Unified, 'tell',       '_tell',       False)
_createPlaceholder(Unified, 'close',      '_close',      False)
_createPlaceholder(Unified, 'flush',      '_flush',      True )
_createPlaceholder(Unified, '__enter__',  '_enter',      True )
_createPlaceholder(Unified, '__exit__',   '_exit',       False)

_createPlaceholder(Unified, 'detach')
_createPlaceholder(Unified, 'isatty')
_createPlaceholder(Unified, 'readinto')
_createPlaceholder(Unified, 'readinto1')
_createPlaceholder(Unified, 'truncate')
_createPlaceholder(Unified, '__iter__')
_createPlaceholder(Unified, '__next__')
