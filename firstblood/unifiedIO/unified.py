import io
import os
import functools
import threading

from .decors import _chainable, _virtual, _weakalias


# TODO: regex readuntil, timeout context, interact, handling non-str
#       universal newline

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
@_virtual('_settimeout')
@_virtual('_underflow')
@_virtual('_readable')
@_virtual('_write')
@_virtual('_writeable')
@_virtual('_writelines')
@_virtual('_fileno')
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
@_weakalias('settimeout')
@_weakalias('readable')
@_weakalias('write')
@_weakalias('writable')
@_weakalias('writeline')
@_weakalias('writelines')
@_weakalias('fileno')
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

    def _writelines(self, lines):
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
        if pos < 0:
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
        """Close the file."""
        if not self.closed: # Recursive Guard
            self.closed = True
            self._close(*args, **kwargs)

    def readlines(self, hint=-1, keep=False):
        """Return a list of lines up to total `hint` bytes from the stream."""
        if hint == 0:
            return []

        if hint < 0:
            return self.read(hint).splitlines(keep)

        res = self.read(hint).splitlines(True)
        if len(res) > 1 and len(res[-1].splitlines(False)[0]) == len(res[-1]):
            self._buffer += res.pop()
        if not keep:
            res = self._empty.join(res).splitlines(False)
        return res

    def lines(self, hint=-1, keep=False):
        """Syntax sugar of readlines and writelines."""
        if isinstance(hint, int):
            return self.readlines(hint, keep)
        return self.writelines(hint)

    def readline(self, size=-1, keep=False):
        """Read until newline or EOF up to `size` bytes."""
        if size == 0:
            return self._empty

        if len(self._buffer):
            s = self.peek(size, imm=True)
            s, t = s.splitlines(True)[0], s.splitlines(False)[0]
            if len(s) > len(t):
                return self._get(len(t), len(s) - len(t), keep, True)

        if size > 0 and len(self._buffer) >= size:
            return self._get(size)

        # TODO: universal newline
        return self.readuntil(self._linesep, size, keep=keep, drop=True, last=True)
    nextline = readline

    def line(self, size=-1, keep=False):
        """Syntax sugar of readline and writeline."""
        if isinstance(size, int):
            return self.readline(size, keep)
        return self.writeline(size)

    def tell(self):
        """Return current stream position."""
        return self._tell() - len(self._buffer)

    def seek(self, *args, **kwargs):
        """Change stream position."""
        if self._seekable():
            self._buffer = self._empty
        self._seek(*args, **kwargs)
        return self

    def read1(self, size=-1):
        """Read and return up to `size` bytes, with at most one read() call"""
        if size == 0:
            return self._empty
        if len(self._buffer):
            return self._get(size)
        if not self._underflow(size):
            raise EOFError('')
        return self._get(size)

    def read(self, size=-1):
        """Read and return exactly `size` bytes."""
        if size == 0:
            return self._empty
        while size < 0 or len(self._buffer) < size:
            if not self._underflow(size - len(self._buffer)):
                if size < 0 and len(self._buffer):
                    break
                raise EOFError('')
        return self._get(size)

    def peek(self, size=-1, imm=False):
        """Peek up to `size` bytes."""
        if size == 0:
            return self._empty
        if not len(self._buffer) and not imm:
            if not self._underflow(size):
                raise EOFError('')
        if size < 0:
            return self._buffer
        return self._buffer[:size]

    def readuntil(self, expected, size=-1, keep=False, drop=True, last=False):
        """Read until `expected` up to `size` bytes."""
        explen = len(expected)
        if not explen:
            raise ValueError('`expected` should not be empty string')
        chunkSZ = max(explen, self._BUFFER_SIZE)

        if size == 0:
            return self._empty

        res = self.peek(size, imm=True)
        pos = res.find(expected)
        if pos != -1:
            return self._get(pos, explen, keep, drop)

        if len(self._buffer) >= size > 0:
            return self._get(size)

        off = max(0, len(self._buffer) - explen)
        while size < 0 or len(self._buffer) < size:
            if not self._underflow(size - len(self._buffer)):
                if not len(self._buffer) or not last:
                    raise EOFError('')
                break
            end = size if size > 0 else len(self._buffer)
            pos = self._buffer[off:end].find(expected)
            if pos != -1:
                return self._get(off + pos, explen, keep, drop)
            off = max(0, len(self._buffer) - explen)
        return self._get(size)
    until = readuntil
    before = functools.partial(readuntil, keep=False, drop=False)
    after = functools.partial(readuntil, keep=False, drop=True)

    def writeline(self, b):
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
