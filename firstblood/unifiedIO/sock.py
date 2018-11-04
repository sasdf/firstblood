import socket
import time
from .unified import UnifiedBase
from .decors import _raw
from .timeout import TimeoutError
from .buffer import RawBuffer, TextBuffer


# --------------------
# Unsupported Virtuals
# --------------------
# @_virtual('_writelines')
# @_virtual('_seek')
# @_virtual('_seekable')
# @_virtual('_tell')
# @_virtual('_enter')
# @_virtual('_exit')
# @_virtual('_iter')
# @_virtual('_next')

# ----------------
# Inherit from raw
# ----------------
@_raw('_close')
@_raw('_fileno')

class UnifiedTCPSock(UnifiedBase):
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
        super().__init__(inpbuf, outbuf)
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
                return False
            inc = self._inpbuf.put(res)
        return True

    def _underflownb(self):
        inc = 0
        while not inc:
            self.raw.settimeout(0)
            try:
                res = self.raw.recv(self._CHUNK_SIZE)
                if not len(res):
                    return False
                inc = self._inpbuf.put(res)
            except BlockingIOError:
                return None
        return True

    def _readable(self):
        return True

    def _overflow(self):
        data = self._outbuf.get()
        return self.raw.sendall(data)

    def _writeable(self):
        return True
