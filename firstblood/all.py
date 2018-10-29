from . import *
from . import patchAll
from . import unifiedIO as uio


patchAll()
if __name__ == '__main__':
    print('[*] Switching to interactive mode')
    from IPython import embed
    embed()
