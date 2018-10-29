from .patch import patch, needFlush


@needFlush
def addMethods():
    targets = [str, bytes, list, tuple, dict, range]
    for t in targets:
        patch(t, 'len', property(t.__len__))
    patch(int, 'len', property(int.bit_length))


@needFlush
def patchMethods():
    pass


@needFlush
def patchAll():
    patchMethods()
    addMethods()


if __name__ == '__main__':
    from IPython import embed
    patchAll()
    embed()
