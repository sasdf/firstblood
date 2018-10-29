import socket
from .unified import UnifiedBase
from .decors import _raw


# --------------------
# Unsupported Virtuals
# --------------------
# @_virtual('_read1')
# @_virtual('_readline')
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
@_raw('_close')

class UnifiedTCPSock(UnifiedBase):
    @classmethod
    def connect(cls, ip, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        return cls(sock)

    def __init__(self, sock):
        super().__init__(binary=True)
        self.raw = sock

    def _read(self, size=-1):
        if size >= 0:
            return self.raw.recv(size)
        else:
            buf = self._empty
            res = ''
            while len(res):
                res = self.raw.recv(self._BUFFER_SIZE)
                buf += res
            return buf

    def _readable(self):
        return True

    def _write(self, data):
        return self.raw.sendall(data)

    def _writeable(self):
        return True
