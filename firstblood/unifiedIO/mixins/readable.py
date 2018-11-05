import io
import functools
import threading
import abc

from .base import BaseMixin


def printable_binary(s):
    return ''.join(
        chr(c)
        if 32 <= c < 127 or c == 0x0a
        else '\\x%02x' % c
        for c in s)


class ReadableMixin(BaseMixin):
    # ---------------
    # Virtual Methods
    # ---------------

    @abc.abstractmethod
    def _underflow(self):
        pass

    def readable(self):
        pass

    # -----------
    # Constructor
    # -----------

    def __init__(self, *, inpbuf, **kwargs):
        super().__init__(**kwargs)
        self._inpbuf = inpbuf
        self.eof = False

    # ---------------
    # Private Methods
    # ---------------

    def _raiseEOF(self):
        self.eof = True
        self._inpbuf.eof()
        raise EOFError('Unexpected end of file.')

    # --------------
    # Public Methods
    # --------------

    def readlines(self, keep=False):
        """Read until EOF and return a list of lines."""
        return self.read().splitlines(keep)

    def readline(self, keep=False):
        """Read until newline or EOF."""
        if self._inpbuf.notempty:
            s = self._inpbuf.get(peek=True)
            # FIXME: Very slow
            s, t = s.splitlines(True)[0], s.splitlines(False)[0]
            if len(s) > len(t):
                return self._inpbuf.get(len(t), len(s) - len(t), keep, True)

        # TODO: universal newline
        return self.readuntil(self._inpbuf.linesep, keep=keep, drop=True, last=True)

    def nextline(self):
        """Seek to next line."""
        self.readline(keep=False)
        return self

    def readexactly(self, size=-1):
        """Read and return exactly `size` bytes."""
        if size == 0:
            return self._inpbuf.null
        while size < 0 or self._inpbuf.size < size:
            if not self._underflow():
                if size < 0 and self._inpbuf.notempty:
                    break
                self._raiseEOF()
        return self._inpbuf.get(size)

    exactly = readexactly
    read = readexactly

    def peek(self, size=-1):
        """Peek up to `size` bytes."""
        if size == 0:
            return self._inpbuf.null
        if self._inpbuf.isempty:
            if not self._underflow():
                self._raiseEOF()
        return self._inpbuf.get(size, peek=True)

    def readuntil(self, expected, keep=False, drop=True, last=False):
        """Read until `expected`."""
        explen = len(expected)
        if not explen:
            raise ValueError('`expected` should not be empty string')

        res = self._inpbuf.get(peek=True)
        pos = res.find(expected)
        if pos != -1:
            return self._inpbuf.get(pos, explen, keep, drop)

        off = max(0, self._inpbuf.size - explen)
        while True:
            if not self._underflow():
                if self._inpbuf.isempty or not last:
                    self._raiseEOF()
                break
            pos = self._inpbuf.after(off).find(expected)
            if pos != -1:
                return self._inpbuf.get(off + pos, explen, keep, drop)
            off = max(0, self._inpbuf.size - explen)
        return self._inpbuf.get()

    until = readuntil
    
    def before(self, expected):
        """Seek before `expected`."""
        self.readuntil(expected, keep=False, drop=False, last=False)
        return self
        
    def after(self, expected):
        """Seek after `expected`."""
        self.readuntil(expected, keep=False, drop=True, last=False)
        return self

    def input(self, prompt=''):
        """
        Print a prompt and read some bytes,
        similar to builtin `input` function.
        """
        return self.write(prompt).readsome()
