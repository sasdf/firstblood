import sys
import functools

from .shortcuts import *
from .file import UnifiedFile
from .sock import UnifiedTCPSock
from .spawn import UnifiedProcess

open = UnifiedFile.open
tcp = UnifiedTCPSock.connect
local = functools.partial(UnifiedTCPSock.connect, 'localhost')
spawn = UnifiedProcess.spawn

stdio = UnifiedFile((sys.stdin, sys.stdout))
stdbio = UnifiedFile((sys.stdin.buffer, sys.stdout.buffer))


if __name__ == '__main__':  # pragma: no cover
    from IPython import embed
    embed()
