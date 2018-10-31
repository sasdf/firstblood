import time
from math import inf


class TimeoutError(Exception):
    def __init__(self, message):
        self.message = message


def toinf(val):
    if val is None:
        return inf
    if val < 0:
        return inf
    return val


class TimeoutContext(object):
    @classmethod
    def initialize(cls, parent):
        self = cls(parent)
        self.timeout = inf
        self.deadline = inf
        self.parent._timeout = self
        return self

    def __init__(self, parent, timeout=None, total=None, overwrite=False):
        self.args = (timeout, total, overwrite)
        self.parent = parent

    @property
    def remaining(self):
        res = min(self.deadline - time.time(), self.timeout)
        # print(f'[+] timeout: {res}')
        if res < 0:
            raise TimeoutError('Timeout before I/O operation')
        if res == inf:
            return None
        return res

    def start(self):
        timeout, total, overwrite = self.args
        self.prev = self.parent._timeout
        timeout, total = toinf(timeout), toinf(total)
        deadline = time.time() + total
        if not overwrite:
            timeout = min(timeout, self.prev.timeout)
            deadline = min(deadline, self.prev.deadline)
        self.timeout = timeout
        self.deadline = deadline
        self.parent._timeout = self

    def stop(self):
        self.parent._timeout = self.prev
        self.parent._timeout.remaining # propagate timeout

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc, *exc_details):
        self.stop()
        if exc is TimeoutError:
            return True
