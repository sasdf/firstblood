import functools as fn

from .patch import patch, needFlush


class wrap:
    def __init__(self, func, prop=False):
        self.func = func
        self.prop=prop

    def __get__(self, this, cls):
        if this is None:
            this = cls
        if self.prop:
            return self.func(this)
        else:
            return fn.partial(self.func, this)


@needFlush
def addMethods():
    patch(object, 'dir', wrap(dir, prop=True))
    patch(object, 'repr', wrap(repr, prop=True))
    patch(object, 'hasattr', wrap(hasattr))
    patch(object, 'getattr', wrap(getattr))
    patch(object, 'setattr', wrap(setattr))


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
