import sys
import io
import select

from .file import UnifiedFile
from .decors import _inherit, _virtual


# --------------------
# Unsupported Virtuals
# --------------------
@_virtual('_iter', override=True)
@_virtual('_next', override=True)
@_virtual('_writelines', override=True)
@_virtual('_fileno', override=True)
@_virtual('_tell', override=True)
@_virtual('_close', override=True)
@_virtual('_enter', '__enter__', override=True)
@_virtual('_exit', '__exit__', override=True)
@_virtual('_seekable', override=True)

# ----------------
# Inherit from raw
# ----------------
@_inherit('_writable', src='out')
@_inherit('_flush', src='out')

# ---------------
# Method Bindings
# ---------------

class UnifiedFileDuplex(UnifiedFile):
    # -----------
    # Constructor
    # -----------

    @classmethod
    def open(cls, *args, **kwargs):
        return cls(io.open(*args, **kwargs))

    def __init__(self, inp, out, name=''):
        super().__init__(inp)
        self._outfile = out
        if 'b' not in out.mode:
            # Assuming TextWrapper
            assert(hasattr(out, 'buffer') and hasattr(out, 'encoding'))
            assert(isinstance(out.encoding, str))
            self.out = out.buffer
            self._rawfile = out
        else:
            assert(not hasattr(out, 'encoding'))
            self.out = out
        self._outencoding = getattr(out, 'encoding', None)

    # ---------------
    # Private Methods
    # ---------------

    def _select(self, read=True, timeout=None):
        args = [[], [], []]
        if read:
            args[0].append(self.raw.fileno())
        else:
            args[1].append(self.out.fileno())
        if timeout is not None and timeout >= 0:
            args.append(timeout)
        res = select.select(*args)
        return sum(map(len, res)) > 0

    # ---------------
    # Virtual Methods
    # ---------------

    def _write(self, data):
        if isinstance(data, str) and self._outencoding is not None:
            data = data.encode(self._outencoding)
        self.out.write(data)

    def isatty(self):
        return self.raw.isatty() and self.out.isatty()


stdio = UnifiedFileDuplex(sys.stdin, sys.stdout)
stdbio = UnifiedFileDuplex(sys.stdin.buffer, sys.stdout.buffer)
