import sys
import functools

from .shortcuts import *
from .file import UnifiedFile
from .sock import UnifiedTCPSock

open = UnifiedFile.open
tcp = UnifiedTCPSock.connect
local = functools.partial(UnifiedTCPSock.connect, 'localhost')
stdio = UnifiedFile((sys.stdin, sys.stdout))
stdbio = UnifiedFile((sys.stdin.buffer, sys.stdout.buffer))


if __name__ == '__main__':
    from IPython import embed
    embed()
