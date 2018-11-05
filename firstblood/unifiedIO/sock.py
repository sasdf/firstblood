import socket

from .mixins import Readable0Mixin, WritableMixin, InteractMixin
from .timeout import TimeoutError
from .buffer import RawBuffer, TextBuffer


class UnifiedTCPSock(InteractMixin, Readable0Mixin, WritableMixin):
    @classmethod
    def connect(cls, ip, port, encoding='utf8'):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        return cls(sock, encoding)

    def __init__(self, sock, encoding='utf8'):
        if encoding is None:
            inpbuf = RawBuffer()
            outbuf = RawBuffer()
        else:
            inpbuf = TextBuffer(encoding=encoding)
            outbuf = RawBuffer(encoding=encoding)
        super().__init__(inpbuf=inpbuf, outbuf=outbuf)
        self.raw = sock

    def _underflow(self):
        inc = 0
        while not inc:
            self.raw.settimeout(self._timeout.remaining)
            try:
                res = self.raw.recv(self._CHUNK_SIZE)
            except (socket.timeout, BlockingIOError):
                raise TimeoutError('Timeout while receiving from socket')
            if not len(res):
                self._inpbuf.eof()
                return False
            inc = self._inpbuf.put(res)
        return True

    def _close(self, *args, **kwargs):
        self.raw.close(*args, **kwargs)
        return True

    def _overflow(self):
        data = self._outbuf.get()
        return self.raw.sendall(data)

    def readable(self):
        return True

    def writable(self):
        return True
