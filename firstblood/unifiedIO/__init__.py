import functools
from .shortcuts import *
from .unified import *
from .file import *
from .sock import *


open = UnifiedFile.open
tcp = UnifiedTCPSock.connect
local = functools.partial(UnifiedTCPSock.connect, 'localhost')


if __name__ == '__main__':
    from IPython import embed
    embed()