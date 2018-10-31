import socket
import time
from .unified import UnifiedBase
from .decors import _raw
from .timeout import TimeoutError


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
        super().__init__(encoding=encoding)
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
            inc = self._buffer.put(res)
        return True

    def _underflownb(self):
        inc = 0
        while not inc:
            self.raw.settimeout(0)
            try:
                res = self.raw.recv(self._CHUNK_SIZE)
                if not len(res):
                    return False
                inc = self._buffer.put(res)
            except BlockingIOError:
                return None
        return True

    def _readable(self):
        return True

    def _write(self, data):
        if isinstance(data, str):
            enc = getattr(self._buffer, 'encoding', 'utf8')
            data = data.encode(enc)
        return self.raw.sendall(data)

    def _writeable(self):
        return True

    def _flush(self):
        return True
