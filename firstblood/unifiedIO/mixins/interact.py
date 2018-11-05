from .readable0 import Readable0Mixin
from .writable import WritableMixin


class InteractMixin(Readable0Mixin, WritableMixin):
    def interact(self):
        from ..interact import interactIO
        print('[*] Switching to interactive mode')
        (cleanupO, stop) = interactIO.pipe(self)
        (cleanupI, _) = self.pipe(interactIO, stop=stop)
        try:
            stop.wait()
            if self.eof:
                raise EOFError('Reach end of file during interactive mode')
            print('[*] Exiting interactive mode')
        except KeyboardInterrupt:
            print('[*] Exiting interactive mode')
        finally:
            stop.set()
            cleanupI()
            cleanupO()
