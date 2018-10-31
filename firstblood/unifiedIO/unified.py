import io
import os
import functools
import threading

from .decors import _chainable, _virtual, _weakalias
from .timeout import TimeoutContext
from .buffer import RawBuffer, TextBuffer

# TODO: regex readuntil, interact, handling non-str, universal newline

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
@_virtual('_underflownb')
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

    def __init__(self, encoding=None):
        self._linesep = os.linesep
        if encoding is None:
            self._buffer = RawBuffer(binary=True)
            self._linesep = self._linesep.encode('utf8')
        else:
            self._buffer = TextBuffer(encoding)
        self._CHUNK_SIZE = io.DEFAULT_BUFFER_SIZE
        self.closed = False
        TimeoutContext.initialize(self)

    # ------------------------
    # Virtual Method Fallbacks
    # ------------------------

    def _writelines(self, lines):
        b = self._buffer.null.join(lines)
        self._write(b)
        return b

    def _enter(self):
        return self

    def _exit(self, *exc_details):
        pass

    # ---------------
    # Private Methods
    # ---------------

    def _raiseEOF(self):
        if isinstance(self._buffer, TextBuffer) and self._buffer.rawsize > 0:
            raise UnicodeDecodeError(
                self._buffer.encoding,
                self._buffer.undecoded,
                0,
                1,
                'Truncated bytes.',
                )
        else:
            raise EOFError('Unexpected end of file.')

    # --------------
    # Public Methods
    # --------------

    def close(self, *args, **kwargs):
        """Close the file."""
        if not self.closed: # Recursive Guard
            self.closed = True
            self._close(*args, **kwargs)

    def readlines(self, keep=False):
        """Read until EOF and return a list of lines."""
        return self.read().splitlines(keep)

    def lines(self, data=None, keep=False):
        """Syntax sugar of readlines and writelines."""
        if data is None:
            return self.readlines(keep)
        return self.writelines(data)

    def readline(self, keep=False):
        """Read until newline or EOF."""
        if self._buffer.notempty:
            s = self._buffer.get(peek=True)
            # FIXME: Very slow
            s, t = s.splitlines(True)[0], s.splitlines(False)[0]
            if len(s) > len(t):
                return self._buffer.get(len(t), len(s) - len(t), keep, True)

        # TODO: universal newline
        return self.readuntil(self._linesep, keep=keep, drop=True, last=True)
    nextline = readline

    def writeline(self, b):
        self._write(b + self._linesep)
        return self

    def line(self, data=None, keep=False):
        """Syntax sugar of readline and writeline."""
        if data is None:
            return self.readline(keep=keep)
        return self.writeline(data)

    def tell(self):
        """Return current stream position."""
        return self._tell() - self._buffer.rawsize

    def seek(self, *args, **kwargs):
        """Change stream position."""
        if self._seekable():
            self._buffer.clear()
        self._seek(*args, **kwargs)
        return self

    def readsome(self):
        """Read and return some bytes"""
        if self._underflownb() == False:
            self._raiseEOF()
        if self._buffer.notempty:
            return self._buffer.get()
        if not self._underflow():
            self._raiseEOF()
        return self._buffer.get()
    some = readsome

    def readeager(self):
        """Read and return all available bytes, block if nothing available."""
        while self._underflownb():
            pass
        if self._buffer.notempty:
            return self._buffer.get()
        if not self._underflow():
            self._raiseEOF()
        while self._underflownb():
            pass
        return self._buffer.get()
    eager = readeager

    def readexactly(self, size=-1):
        """Read and return exactly `size` bytes."""
        if size == 0:
            return self._buffer.null
        while size < 0 or self._buffer.size < size:
            if not self._underflow():
                if size < 0 and self._buffer.notempty:
                    break
                self._raiseEOF()
        return self._buffer.get(size)
    exactly = readexactly
    read = readexactly

    def peek(self, size=-1):
        """Peek up to `size` bytes."""
        if size == 0:
            return self._buffer.null
        if self._buffer.isempty:
            if not self._underflow():
                self._raiseEOF()
        return self._buffer.get(size, peek=True)

    def readuntil(self, expected, keep=False, drop=True, last=False):
        """Read until `expected` up to `size` bytes."""
        explen = len(expected)
        if not explen:
            raise ValueError('`expected` should not be empty string')

        res = self._buffer.get(peek=True)
        pos = res.find(expected)
        if pos != -1:
            return self._buffer.get(pos, explen, keep, drop)

        off = max(0, self._buffer.size - explen)
        while True:
            if not self._underflow():
                if self._buffer.isempty or not last:
                    self._raiseEOF()
                break
            pos = self._buffer.after(off).find(expected)
            if pos != -1:
                return self._buffer.get(off + pos, explen, keep, drop)
            off = max(0, self._buffer.size - explen)
        return self._buffer.get()
    until = readuntil
    before = functools.partial(readuntil, keep=False, drop=False)
    after = functools.partial(readuntil, keep=False, drop=True)

    def timeout(self, timeout=None, total=None, overwrite=False):
        return TimeoutContext(self, timeout, total, overwrite)


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
