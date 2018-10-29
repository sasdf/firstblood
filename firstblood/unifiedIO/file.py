import io
from .unified import UnifiedBase
from .decors import _raw


# --------------------
# Unsupported Virtuals
# --------------------
# @_virtual('_iter')
# @_virtual('_next')

# ----------------
# Inherit from raw
# ----------------

@_raw('_read')
@_raw('_read1')
@_raw('_readable')
@_raw('_readline')
@_raw('_write')
@_raw('_writable')
@_raw('_writelines')
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

@_raw('fileno', 'fileno')
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
