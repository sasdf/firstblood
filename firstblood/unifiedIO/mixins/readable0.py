import threading

from .timeout import TimeoutMixin
from .readable import ReadableMixin


class Readable0Mixin(TimeoutMixin, ReadableMixin):
    def readlazy(self):
        """Read and return some bytes"""
        if self._inpbuf.notempty:
            return self._inpbuf.get()
        with self.timeout(0):
            if not self._underflow():
                self._raiseEOF()
        if self._inpbuf.notempty:
            return self._inpbuf.get()
        if not self._underflow():
            self._raiseEOF()
        return self._inpbuf.get()

    lazy = readlazy

    def readeager(self):
        """Read and return all available bytes, block if nothing available."""
        with self.timeout(0):
            while self._underflow():
                pass
        if self._inpbuf.notempty:
            return self._inpbuf.get()
        if not self._underflow():
            self._raiseEOF()
        with self.timeout(0):
            while self._underflow():
                pass
        return self._inpbuf.get()

    eager = readeager
    some = readsome = readeager

    def pipe(self, dest, block=False, stop=None):
        """Create another thread for handling the stream."""
        stop = stop or threading.Event()

        def worker():
            try:
                while not stop.is_set():
                    with self.timeout(total=0.1):
                        data = self.readlazy()
                        dest.write(data)
                return False
            except EOFError:
                stop.set()
                return True

        if block:
            return worker()
        else:
            thr = threading.Thread(target=worker)
            thr.start()

            def cleanup():
                stop.set()
                thr.join()

            return (cleanup, stop)
