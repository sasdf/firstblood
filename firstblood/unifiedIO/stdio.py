import sys
import io
import select

from .unified import UnifiedBase
from .timeout import TimeoutError
from .buffer import RawBuffer, TextBuffer
from .decors import _inherit


# --------------------
# Unsupported Virtuals
# --------------------

# ----------------
# Inherit from raw
# ----------------
@_inherit('_writable', src='out')
@_inherit('_readable', src='inp')

# ---------------
# Method Bindings
# ---------------

class UnifiedFileDuplex(UnifiedBase):
    # -----------
    # Constructor
    # -----------

    def __init__(self, inp, out, name=''):
        if 'b' not in inp.mode:
            # Assuming TextWrapper
            assert(hasattr(inp, 'buffer') and hasattr(inp, 'encoding'))
            assert(isinstance(inp.encoding, str))
            inpbuf = TextBuffer(inp.encoding)
            self.inp = inp.buffer
            self._inpfile = inp
        else:
            assert(not hasattr(inp, 'encoding'))
            inpbuf = RawBuffer()
            self.inp = inp
        self._input1 = self.inp.read1
            
        if 'b' not in out.mode:
            # Assuming TextWrapper
            assert(hasattr(out, 'buffer') and hasattr(out, 'encoding'))
            assert(isinstance(out.encoding, str))
            outbuf = RawBuffer(out.encoding)
            self.out = out.buffer
            self._outfile = out
        else:
            assert(not hasattr(out, 'encoding'))
            outbuf = RawBuffer()
            self.out = out
            
        self.closed = inp.closed or out.closed
        self.name = name
        
        super().__init__(inpbuf, outbuf)

    # ---------------
    # Private Methods
    # ---------------

    def _select(self, read=True, timeout=None):
        args = [[], [], []]
        if read:
            args[0].append(self.inp.fileno())
        else:
            args[1].append(self.out.fileno())
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
                inc = self._inpbuf.put(res)
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
                inc = self._inpbuf.put(res)
            else:
                return None
        return True

    def _overflow(self):
        data = self._outbuf.get()
        self.out.write(data)
        self.out.flush()

stdio = UnifiedFileDuplex(sys.stdin, sys.stdout)
stdbio = UnifiedFileDuplex(sys.stdin.buffer, sys.stdout.buffer)
