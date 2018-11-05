import abc

from .base import BaseMixin


class SeekableMixin(BaseMixin):
    @abc.abstractmethod
    def _seek(self, pos):
        pass

    @abc.abstractmethod
    def seekable(self):
        pass

    def seek(self, *args, **kwargs):
        """Change stream position."""
        self._seek(*args, **kwargs)
        self.eof = False
        self._inpbuf.clear()
        return self
