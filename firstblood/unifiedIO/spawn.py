from subprocess import Popen, PIPE, TimeoutExpired

from .mixins import InteractMixin
from .file import ReadableFileMixin, WritableFileMixin
from .buffer import RawBuffer, TextBuffer
from .timeout import TimeoutError


class UnifiedProcess(InteractMixin, ReadableFileMixin, WritableFileMixin):
    @classmethod
    def spawn(cls, args, encoding='utf8'):
        if isinstance(args, str):
            proc = Popen(args, stdin=PIPE, stdout=PIPE, shell=True)
        else:
            proc = Popen(args, stdin=PIPE, stdout=PIPE)
        return cls(proc, encoding)

    def __init__(self, proc, encoding='utf8'):
        if encoding is None:
            inpbuf = RawBuffer()
            outbuf = RawBuffer()
        else:
            inpbuf = TextBuffer(encoding=encoding)
            outbuf = RawBuffer(encoding=encoding)
        self.encoding = encoding
        self.inp = proc.stdout
        self.out = proc.stdin
        self.proc = proc
        super().__init__(inpbuf=inpbuf, outbuf=outbuf)

    def wait(self):
        try:
            return self.proc.wait(self._timeout.remaining)
        except TimeoutExpired:
            raise TimeoutError('Timeout when wait the process to terminate')

    def _close(self, dir=None):
        if dir is None:
            self.proc.stdin.close()
            self.proc.stdout.close()
        elif dir in ['out', 'write', 'send']:
            # FIXME: Use communicate instead
            self.proc.stdin.close()
        elif dir in ['in', 'read', 'recv']:
            self.proc.stdout.close()
        else:
            raise KeyError(
                "direction must be in "
                "['in', 'out', 'read', 'recv', 'send', 'write']"
                )
        if dir is None:
            return self.wait()

    def _exit(self, *exc_details):
        self.kill()
        self.close()

    def kill(self):
        self.proc.kill()
        return self.wait()

    def terminate(self):
        self.proc.terminate()
        return self.wait()

    def signal(self, sig):
        return self.proc.send_signal(sig)

    @property
    def pid(self):
        return self.proc.pid

    @property
    def returncode(self):
        return self.proc.returncode
