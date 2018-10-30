import socket
from .unified import UnifiedBase
from .decors import _raw


# --------------------
# Unsupported Virtuals
# --------------------
# @_virtual('_writelines')
# @_virtual('_seek')
# @_virtual('_seekable')
# @_virtual('_tell')
# @_virtual('_flush')
# @_virtual('_enter')
# @_virtual('_exit')
# @_virtual('_iter')
# @_virtual('_next')

# ----------------
# Inherit from raw
# ----------------
@_raw('_settimeout')
@_raw('_close')
@_raw('_fileno')

class UnifiedTCPSock(UnifiedBase):
    @classmethod
    def connect(cls, ip, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        return cls(sock)

    def __init__(self, sock):
        super().__init__(binary=True)
        self.raw = sock

    def _underflow(self, size=-1):
        size = max(size, self._BUFFER_SIZE)
        res = self.raw.recv(size)
        if not len(res):
            return False
        self._buffer += res
        return True

    def _readable(self):
        return True

    def _write(self, data):
        return self.raw.sendall(data)

    def _writeable(self):
        return True
