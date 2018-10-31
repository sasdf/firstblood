import io
import select
from .unified import UnifiedBase
from .decors import _raw
from .timeout import TimeoutError


# --------------------
# Unsupported Virtuals
# --------------------
# @_virtual('_settimeout')
# @_virtual('_iter')
# @_virtual('_next')

# ----------------
# Inherit from raw
# ----------------

@_raw('_readable')
@_raw('_write')
@_raw('_writable')
@_raw('_writelines')
@_raw('_fileno')
@_raw('_seek')
@_raw('_seekable')
@_raw('_tell')
@_raw('_flush')
@_raw('_close')
@_raw('_enter', '__enter__')
@_raw('_exit', '__exit__')

# ---------------
# Method Bindings
# ---------------

@_raw('isatty', 'isatty')
@_raw('mode', 'mode', prop=True)
@_raw('name', 'name', prop=True)
@_raw('truncate', 'truncate')

class UnifiedFile(UnifiedBase):
    # -----------
    # Constructor
    # -----------

    @classmethod
    def open(cls, *args, **kwargs):
        return cls(io.open(*args, **kwargs))

    def __init__(self, file):
        binary = 'b' in file.mode

        # Variables - public
        if not binary:
            # Assuming TextWrapper
            assert(hasattr(file, 'buffer') and hasattr(file, 'encoding'))
            assert(isinstance(file.encoding, str))
            super().__init__(encoding=file.encoding)
            self.raw = file.buffer
            self._rawfile = file
        else:
            assert(not hasattr(file, 'encoding'))
            self.raw = file
        self.closed = file.closed
        self._input1 = self.raw.read1

    # ---------------
    # Private Methods
    # ---------------

    def _select(self, read=True, timeout=None):
        args = [[], [], []]
        if read:
            args[0].append(self._fileno())
        else:
            args[1].append(self._fileno())
        if timeout is not None and timeout >= 0:
            args.append(timeout)
        res = select.select(*args)
        return sum(map(len, res)) > 0

    # ---------------
    # Virtual Methods
    # ---------------

    def _underflow(self):
        inc = 0
        while not inc:
            if self._select(timeout=self._timeout.remaining):
                res = self._input1(self._CHUNK_SIZE)
                if not len(res):
                    return False
                inc = self._buffer.put(res)
            else:
                raise TimeoutError('Timeout while reading file')
        return True

    def _underflownb(self):
        inc = 0
        while not inc:
            if self._select(timeout=0):
                res = self._input1(self._CHUNK_SIZE)
                if not len(res):
                    return False
                inc = self._buffer.put(res)
            else:
                return None
        return True
