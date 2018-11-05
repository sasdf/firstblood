import io
import select

from .mixins import Readable0Mixin, WritableMixin, SeekableMixin
from .timeout import TimeoutError
from .buffer import RawBuffer, TextBuffer


def _createBuffer(f, read=True):
    if 'b' in f.mode:
        assert(not hasattr(f, 'encoding'))
        buf = RawBuffer()
        raw = f
    else:
        # Assuming TextWrapper
        assert(hasattr(f, 'buffer') and hasattr(f, 'encoding'))
        assert(isinstance(f.encoding, str))
        if read:
            buf = TextBuffer(f.encoding)
        else:
            buf = RawBuffer(f.encoding)
        raw = f.buffer
    return (raw, buf)


def _select(f, read=True, timeout=None):
    args = [[], [], []]
    if read:
        args[0].append(f.fileno())
    else:
        args[1].append(f.fileno())
    if timeout is not None and timeout >= 0:
        args.append(timeout)
    res = select.select(*args)
    return sum(map(len, res)) > 0


class ReadableFileMixin(Readable0Mixin):
    def _close(self):
        return self.inp.close()

    def _underflow(self):
        inc = 0
        while not inc:
            if _select(self.inp, read=True, timeout=self._timeout.remaining):
                res = self.inp.read1(self._CHUNK_SIZE)
                if not len(res):
                    return False
                inc = self._inpbuf.put(res)
            else:
                raise TimeoutError('Timeout while reading f')
        return True

    def readable(self):
        return True


class WritableFileMixin(WritableMixin):
    def _close(self):
        return self.out.close()

    def _overflow(self):
        data = self._outbuf.get()
        self.out.write(data)
        self.out.flush()

    def writable(self):
        return True


class UnifiedFileDuplex(ReadableFileMixin, WritableFileMixin):
    def __init__(self, *, inp, out, **kwargs):
        inpraw, inpbuf = _createBuffer(inp, read=True)
        outraw, outbuf = _createBuffer(out, read=False)
        self.inp = inpraw
        self.out = outraw
        self._inpfile = inp
        self._outfile = out
        super().__init__(inpbuf=inpbuf, outbuf=outbuf, **kwargs)

    def _close(self):
        return super()._close()


class UnifiedReadableFile(SeekableMixin, ReadableFileMixin):
    def __init__(self, *, inp, **kwargs):
        raw, buf = _createBuffer(inp, read=True)
        self.inp = raw
        self._inpfile = inp
        super().__init__(inpbuf=buf, **kwargs)

    def _seek(self, *args, **kwargs):
        return self.inp.seek(*args, **kwargs)

    def seekable(self):
        return True


class UnifiedWritableFile(SeekableMixin, WritableFileMixin):
    def __init__(self, *, out, **kwargs):
        raw, buf = _createBuffer(out, read=False)
        self.out = raw
        self._outfile = out
        super().__init__(outbuf=buf, **kwargs)

    def _seek(self, *args, **kwargs):
        return self.out.seek(*args, **kwargs)

    def seekable(self):
        return True


class UnifiedRWFile(UnifiedReadableFile, UnifiedWritableFile):
    def __init__(self, *, f):
        super().__init__(inp=f, out=f)

    def _seek(self, *args, **kwargs):
        return super()._seek(*args, **kwargs)

    def _close(self):
        return super()._close()


def UnifiedFile(f):
    if isinstance(f, tuple):
        if len(f) != 2:
            raise ValueError('Need to be a 2-tuple of I/O pair.')
        inp, out = f
        return UnifiedFileDuplex(inp=inp, out=out)
    elif f.readable() and f.writable():
        return UnifiedRWFile(f=f)
    elif f.readable():
        return UnifiedReadableFile(inp=f)
    elif f.writable():
        return UnifiedWritableFile(out=f)


def UnifiedFileOpen(*args, **kwargs):
    return UnifiedFile(open(*args, **kwargs))


UnifiedFile.open = UnifiedFileOpen
