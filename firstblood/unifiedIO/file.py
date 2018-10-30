import io
import select
from .unified import UnifiedBase
from .decors import _raw


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
        super().__init__(binary=binary)

        # Variables - public
        self.raw = file
        self.closed = file.closed
        if hasattr(self.raw, 'read1'):
            self._input1 = self.raw.read1
        else:
            self._input1 = self.raw.read

    # ---------------
    # Private Methods
    # ---------------

    def _select(self, read=True):
        args = [[], [], []]
        if read:
            args[0].append(self._fileno())
        else:
            args[1].append(self._fileno())
        if timeout >= 0:
            args.append(timeout)
        res = select.select(*args)
        return sum(map(len, res)) > 0

    # ---------------
    # Virtual Methods
    # ---------------

    def _underflow(self, size=-1):
        size = max(size, self._BUFFER_SIZE)
        res = self._input1(size)
        if not len(res):
            return False
        self._buffer += res
        return True
