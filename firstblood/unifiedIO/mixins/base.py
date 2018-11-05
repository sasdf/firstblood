import io
import abc


class BaseMixin(abc.ABC):
    # -----------
    # Constructor
    # -----------

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._CHUNK_SIZE = io.DEFAULT_BUFFER_SIZE
        self.closed = False

    # ---------------
    # Virtual Methods
    # ---------------

    @abc.abstractmethod
    def _close(self):
        pass

    def _enter(self):
        return self

    def _exit(self, *exc_details):
        pass

    # --------------
    # Public Methods
    # --------------

    def close(self, *args, **kwargs):
        """Close the file."""
        if not self.closed:  # Recursive Guard
            self.closed = True
            self._close(*args, **kwargs)

    def lines(self, data=None, keep=False):
        """Syntax sugar of readlines and writelines."""
        if data is None:
            return self.readlines(keep)
        return self.writelines(data)

    def line(self, data=None, keep=False):
        """Syntax sugar of readline and writeline."""
        if data is None:
            return self.readline(keep=keep)
        return self.writeline(data)

    def __enter__(self, *args, **kwargs):
        self._enter(*args, **kwargs)
        return self

    def __exit__(self, *args, **kwargs):
        self._exit(*args, **kwargs)
        if not self.closed:  # Recursive guard
            self.close()
