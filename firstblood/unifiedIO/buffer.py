import codecs


class RawBuffer(object):
    def __init__(self, binary=True):
        if binary:
            self._buffer = b''
            self.null = b''
        else:
            self._buffer = ''
            self.null = ''

    @property
    def notempty(self):
        return len(self) > 0

    @property
    def isempty(self):
        return len(self) == 0

    @property
    def size(self):
        return len(self)

    @property
    def rawsize(self):
        return len(self)

    def get(self, pos=-1, needle=0, keep=False, drop=True, peek=False):
        if pos < 0:
            res = self._buffer
            if not peek:
                self._buffer = self.null
            return res
        if keep:
            left, right = pos + needle, pos + needle
        elif drop:
            left, right = pos, pos + needle
        else:
            left, right = pos, pos
        res = self._buffer[:left]
        if not peek:
            self._buffer = self._buffer[right:]
        return res

    def after(self, pos):
        return self._buffer[pos:]

    def unget(self, data):
        self._buffer = data + self._buffer

    def put(self, data):
        self._buffer += data
        return len(data)

    def clear(self):
        self._buffer = self.null

    def __len__(self):
        return len(self._buffer)


class TextBuffer(RawBuffer):
    def __init__(self, encoding):
        self._buffer = ''
        self.encoding = encoding
        self._encoder = codecs.getencoder(encoding)
        self._decoder = codecs.getincrementaldecoder(encoding)()
        self.null = ''

    @property
    def undecoded(self):
        return self._decoder.getstate()[0]

    @property
    def rawsize(self):
        # FIXME: Unreliable and slow
        raw, consumed = self._encoder(self._buffer)
        return len(raw) + len(self.undecoded)

    def put(self, data):
        res = self._decoder.decode(data)
        self._buffer += res
        return len(res)

    def clear(self):
        self._buffer = self.null
        self._decoder.reset()
