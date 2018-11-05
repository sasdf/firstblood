import codecs
import io
import sys
import os

from .file import ReadableFileMixin, WritableFileMixin
from .buffer import RawBuffer


class EscapeDecoder(codecs.IncrementalDecoder):
    def __init__(self, errors='strict', encoding='utf8'):
        self.encoding = encoding
        self.reset()

    def decode(self, obj, final=False):
        self.buffer += obj
        res = b''
        while True:
            pos = self.buffer.find('\\')
            if pos == -1:
                res += self.buffer.encode(self.encoding)
                self.buffer = ''
                break

            res += self.buffer[:pos].encode(self.encoding)
            self.buffer = self.buffer[pos:]

            if len(self.buffer) < 2:
                break

            if self.buffer[1] == '\\':
                res += b'\\'
                self.buffer = self.buffer[2:]
            elif self.buffer[1] == '0':
                res += b'\0'
                self.buffer = self.buffer[2:]
            elif self.buffer[1] == 'x':
                if len(self.buffer) < 4:
                    break
                res += bytes([int(self.buffer[2:4], 16)])
                self.buffer = self.buffer[4:]
            elif self.buffer[1] == '#':
                end = self.buffer.find('#', 2)
                if end == -1:
                    break
                ret = eval(self.buffer[2: end])
                if isinstance(ret, str):
                    ret = ret.encode(self.encoding)
                res += ret
                self.buffer = self.buffer[end+1:]
            else:
                self.buffer = self.buffer[1:]
        if final and len(self.buffer):
            raise UnicodeDecodeError(
                'escape-seq',
                self.buffer.decode(self.encoding),
                0,
                len(self.buffer),
                'Truncated bytes.',
            )
        return res

    def reset(self):
        self.buffer = ''

    def getstate(self):
        return (self.buffer, 0)

    def setstate(self, state):
        self.buffer = state[0]


class EscapeEncoder(codecs.IncrementalEncoder):
    def __init__(self, errors='strict', encoding='utf8'):
        self.encoding = encoding
        self.reset()

    def encode(self, obj, final=False):
        if isinstance(obj, str):
            obj = obj.encode(self.encoding)
        res = ''
        for c in obj:
            if 32 <= c < 127 and c != 92:
                res += chr(c)
            elif c == 10:
                res += '\n'
            elif c == 92:
                res += '\\\\'
            elif c < 256:
                res += '\\x%02x' % c
            else:
                raise ValueError('bytes must in range(0, 256)')
        return res.encode(self.encoding)

    def reset(self):
        pass

    def getstate(self):
        return 0

    def setstate(self, state):
        pass


class InteractInputBuffer(RawBuffer):
    def __init__(self, encoding='utf8'):
        self._buffer = b''
        self.encoding = encoding
        self._decoder = EscapeDecoder(encoding=encoding)
        self.null = b''
        self.linesep = os.linesep.encode(encoding)
        self.datatype = bytes

    def put(self, data):
        if isinstance(data, bytes):
            data = data.decode(self.encoding)
        res = self._decoder.decode(data)
        self._buffer += res
        return len(res)


class InteractOutputBuffer(RawBuffer):
    def __init__(self, encoding='utf8'):
        self._buffer = b''
        self.encoding = 'escape-seq'
        self._encoder = EscapeEncoder(encoding=encoding)
        self.null = b''
        self.linesep = os.linesep
        self.datatype = bytes

    def put(self, data):
        res = self._encoder.encode(data)
        self._buffer += res
        return len(res)


class UnifiedInteract(ReadableFileMixin, WritableFileMixin):
    # -----------
    # Constructor
    # -----------

    def __init__(self):
        self.out = sys.stdout.buffer
        self.inp = sys.stdin.buffer
        inpbuf = InteractInputBuffer()
        outbuf = InteractOutputBuffer()
        super().__init__(inpbuf=inpbuf, outbuf=outbuf)

    def _close(self):
        raise io.UnsupportedOperation()

interactIO = UnifiedInteract()
