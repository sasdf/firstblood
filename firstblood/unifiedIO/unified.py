import io
import functools
import threading

from .decors import _chainable, _virtual, _weakalias
from .timeout import TimeoutContext

# TODO: regex readuntil, handling non-str, universal newline


def printable_binary(s):
    return ''.join(
        chr(c)
        if 32 <= c < 127 or c == 0x0a
        else '\\x%02x' % c
        for c in s)


# ---------
# Chainable
# ---------
@_chainable('write')
@_chainable('writeline')
@_chainable('writelines')
@_chainable('seek')
@_chainable('nextline')
@_chainable('before')
@_chainable('after')
# ----------------
# Virtuals Methods
# ----------------
@_virtual('_underflow')
@_virtual('_underflownb')
@_virtual('_overflow')
@_virtual('_readable')
@_virtual('_writeable')
@_virtual('_fileno')
@_virtual('_seek')
@_virtual('_seekable')
@_virtual('_tell')
@_virtual('_close')
@_virtual('_enter')
@_virtual('_exit')
@_virtual('_iter')
@_virtual('_next')
# -------------
# Virtual Alias
# -------------
@_weakalias('settimeout')
@_weakalias('readable')
@_weakalias('writable')
@_weakalias('fileno')
@_weakalias('seek')
@_weakalias('seekable')
@_weakalias('tell')
@_weakalias('close')
class UnifiedBase(object):
    # -----------
    # Constructor
    # -----------

    def __init__(self, inpbuf, outbuf):
        self._inpbuf = inpbuf
        self._outbuf = outbuf
        self._CHUNK_SIZE = io.DEFAULT_BUFFER_SIZE
        self.closed = False
        TimeoutContext.initialize(self)

    # ------------------------
    # Virtual Method Fallbacks
    # ------------------------

    def _enter(self):
        return self

    def _exit(self, *exc_details):
        pass

    # ---------------
    # Private Methods
    # ---------------

    def _raiseEOF(self):
        self._inpbuf.eof()
        raise EOFError('Unexpected end of file.')

    # --------------
    # Public Methods
    # --------------

    def close(self, *args, **kwargs):
        """Close the file."""
        if not self.closed:  # Recursive Guard
            self.closed = True
            self._close(*args, **kwargs)

    def readlines(self, keep=False):
        """Read until EOF and return a list of lines."""
        return self.read().splitlines(keep)

    def writelines(self, lines):
        """Write array of lines."""
        for line in lines:
            self._outbuf.put(line)
            self._outbuf.endl()
        self._overflow()

    def lines(self, data=None, keep=False):
        """Syntax sugar of readlines and writelines."""
        if data is None:
            return self.readlines(keep)
        return self.writelines(data)

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

    nextline = readline

    def writeline(self, b):
        self._outbuf.put(b)
        self._outbuf.endl()
        self._overflow()

    def line(self, data=None, keep=False):
        """Syntax sugar of readline and writeline."""
        if data is None:
            return self.readline(keep=keep)
        return self.writeline(data)

    def tell(self):
        """Return current stream position."""
        return self._tell() - self._inpbuf.rawsize

    def seek(self, *args, **kwargs):
        """Change stream position."""
        if self._seekable():
            self._inpbuf.clear()
        self._seek(*args, **kwargs)
        return self

    def readeager(self):
        """Read and return all available bytes, block if nothing available."""
        while self._underflownb():
            pass
        if self._inpbuf.notempty:
            return self._inpbuf.get()
        if not self._underflow():
            self._raiseEOF()
        while self._underflownb():
            pass
        return self._inpbuf.get()

    eager = readeager
    some = readsome = readeager

    def readlazy(self):
        """Read and return some bytes"""
        if self._inpbuf.notempty:
            return self._inpbuf.get()
        if self._underflownb() is False:
            self._raiseEOF()
        if self._inpbuf.notempty:
            return self._inpbuf.get()
        if not self._underflow():
            self._raiseEOF()
        return self._inpbuf.get()

    lazy = readlazy

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
        """Read until `expected` up to `size` bytes."""
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
    before = functools.partial(readuntil, keep=False, drop=False)
    after = functools.partial(readuntil, keep=False, drop=True)

    def input(self, prompt=''):
        """
        Print a prompt and read some bytes,
        similar to builtin `input` function.
        """
        return self.write(prompt).readsome()

    def write(self, data):
        """Write string to stream."""
        self._outbuf.put(data)
        self._overflow()

    def timeout(self,
                timeout=None,
                total=None,
                overwrite=False,
                propagate=False):
        """Create a timeout context."""
        return TimeoutContext(self, timeout, total, overwrite, propagate)

    def pipe(self, dest, block=False, stop=None):
        """Create another thread for handling the stream."""
        stop = stop or threading.Event()

        def worker():
            try:
                while not stop.is_set():
                    with self.timeout(total=0.1):
                        data = self.readlazy()
                        dest.write(data)
                return False
            except EOFError:
                stop.set()
                return True

        if block:
            return worker()
        else:
            thr = threading.Thread(target=worker)
            thr.start()

            def cleanup():
                stop.set()
                thr.join()

            return (cleanup, stop)

    def interact(self):
        from .stdio import stdio
        print('[*] Switching to interactive mode')
        (cleanup, stop) = stdio.pipe(self)
        try:
            while not stop.is_set():
                with self.timeout(total=0.1):
                    data = self.readlazy()
                    if isinstance(data, bytes):
                        data = printable_binary(data)
                    stdio.write(data)
            print('[*] Exiting interactive mode')
        except EOFError:
            raise EOFError('Reach end of file during interactive mode')
        except KeyboardInterrupt:
            print('[*] Exiting interactive mode')
        finally:
            stop.set()
            cleanup()

    def __enter__(self, *args, **kwargs):
        self._enter(*args, **kwargs)
        return self

    def __exit__(self, *args, **kwargs):
        self._exit(*args, **kwargs)
        if not self.closed:  # Recursive guard
            self.close()
