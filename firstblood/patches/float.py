import math
from .patch import patch, needFlush


def tofixed(n, s):
    return f'%.{s}f' % n


@needFlush
def addMethods():
    patch(float, 'int', property(int))
    patch(float, 'str', property(str))
    patch(float, 'fixed', tofixed)
    patch(float, 'ceil', property(math.ceil))
    patch(float, 'floor', property(math.floor))
    patch(float, 'round', property(round))


@needFlush
def patchMethods():
    pass


@needFlush
def patchAll():
    addMethods()
    patchMethods()


if __name__ == '__main__':
    from IPython import embed
    patchAll()
    embed()
