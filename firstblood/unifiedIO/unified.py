import io
import os
import functools
import threading
from math import inf

from .decors import _chainable, _virtual, _weakalias


# TODO: regex readuntil, timeout, interact, handling non-str

# ---------
# Chainable
# ---------
@_chainable('write')
@_chainable('writeline')
@_chainable('writelines')
@_chainable('seek')
@_chainable('flush')
@_chainable('nextline')
@_chainable('before')
@_chainable('after')

# ----------------
# Virtuals Methods
# ----------------
@_virtual('_read')
@_virtual('_read1')
@_virtual('_readable')
@_virtual('_readline')
@_virtual('_write')
@_virtual('_writeable')
@_virtual('_writelines')
@_virtual('_seek')
@_virtual('_seekable')
@_virtual('_tell')
@_virtual('_close')
@_virtual('_flush')
@_virtual('_enter')
@_virtual('_exit')
@_virtual('_iter')
@_virtual('_next')

# -------------
# Virtual Alias
# -------------
@_weakalias('read')
@_weakalias('read1')
@_weakalias('readable')
@_weakalias('readline')
@_weakalias('write')
@_weakalias('writable')
@_weakalias('writeline')
@_weakalias('writelines')
@_weakalias('seek')
@_weakalias('seekable')
@_weakalias('tell')
@_weakalias('close')
@_weakalias('flush')

class UnifiedBase(object):
    # -----------
    # Constructor
    # -----------

    def __init__(self, binary=False):
        self._buffer = ''
        self._empty = ''
        self._linesep = os.linesep
        self._BUFFER_SIZE = io.DEFAULT_BUFFER_SIZE
        self.closed = False
        if binary:
            self._buffer = self._buffer.encode('utf8')
            self._empty = self._empty.encode('utf8')
            self._linesep = self._linesep.encode('utf8')

    # ------------------------
    # Virtual Method Fallbacks
    # ------------------------

    def _read1(self, size=-1, timeout=-1):
        if size < 0:
            size = self._BUFFER_SIZE
        return self._read(size)

    def _readline(self, size=-1, timeout=-1):
        return self.readuntil(self._linesep, size, keep=True, drop=True)

    def _writelines(self, lines, timeout=-1):
        b = self._empty.join(lines)
        self._write(b)
        return b

    def _enter(self):
        return self

    def _exit(self, *exc_details):
        pass

    # ---------------
    # Private Methods
    # ---------------

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

    # --------------
    # Public Methods
    # --------------

    def close(self, *args, **kwargs):
        if not self.closed: # Recursive Guard
            self.closed = True
            self._close(*args, **kwargs)

    def readlines(self, hint=-1, keep=False, timeout=-1):
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

    def lines(self, hint=-1, keep=False, timeout=-1):
        if isinstance(hint, int):
            return self.readlines(hint, keep)
        return self.writelines(hint)

    def readline(self, size=-1, keep=False, timeout=-1):
        if size == 0:
            return self._empty

        if len(self._buffer):
            s = self.peek(size, timeout=0)
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
    nextline = readline

    def line(self, size=-1, keep=False, timeout=-1):
        if isinstance(size, int):
            return self.readline(size, keep)
        return self.writeline(size)

    def tell(self):
        return self._tell() - len(self._buffer)

    def seek(self, *args, **kwargs):
        if self._seekable():
            self._buffer = self._empty
        self._seek(*args, **kwargs)
        return self

    def read1(self, size=-1, timeout=-1):
        if size == 0:
            return self._empty
        if len(self._buffer):
            return self._get(size)
        return self._read1(size)

    def read(self, size=-1, timeout=-1):
        if size == 0:
            return self._empty
        if size > 0 and len(self._buffer) >= size:
            return self._get(size)
        res = self._get()
        res += self._read(size - len(res))
        return res

    def peek(self, size=-1, timeout=-1):
        if size == 0:
            return self._empty
        if not len(self._buffer) and timeout != 0:
            self.buffer += self.read1(size)
        if size is inf or size < 0:
            return self._buffer
        return self._buffer[:size]

    def readuntil(self, expected, size=-1, keep=False, drop=True, timeout=-1):
        explen = len(expected)
        if not explen:
            raise ValueError('`expected` should not be empty string')
        chunkSZ = max(explen, self._BUFFER_SIZE)

        if size < 0:
            size = inf

        res = self.peek(size, timeout=0)
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
    before = functools.partial(readuntil, keep=False, drop=False)
    after = functools.partial(readuntil, keep=False, drop=True)

    def writeline(self, b, timeout=-1):
        self._write(b + self._linesep)
        return self

    def interact(self):
        # TODO
        pass

    def __enter__(self, *args, **kwargs):
        self._enter(*args, **kwargs)
        return self

    def __exit__(self, *args, **kwargs):
        self._exit(*args, **kwargs)
        if not self.closed: # Recursive guard
            self.close()
