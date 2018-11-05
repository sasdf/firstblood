import abc

from .base import BaseMixin


class WritableMixin(BaseMixin):
    # -----------
    # Constructor
    # -----------

    def __init__(self, *, outbuf, **kwargs):
        super().__init__(**kwargs)
        self._outbuf = outbuf

    # ---------------
    # Virtual Methods
    # ---------------

    @abc.abstractmethod
    def _overflow(self):
        pass

    @abc.abstractmethod
    def writable(self):
        pass

    # --------------
    # Public Methods
    # --------------

    def write(self, b):
        """Write string to stream."""
        self._outbuf.put(b)
        self._overflow()
        return self

    def endl(self):
        """Write a newline to stream."""
        self._outbuf.endl()
        self._overflow()
        return self

    def writelines(self, lines):
        """Write array of lines."""
        for line in lines:
            self._outbuf.put(line)
            self._outbuf.endl()
        self._overflow()
        return self

    def writeline(self, b):
        self._outbuf.put(b)
        self._outbuf.endl()
        self._overflow()
        return self
