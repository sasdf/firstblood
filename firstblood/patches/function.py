import functools as fn
from types import FunctionType, BuiltinFunctionType
from .patch import patch, needFlush


@needFlush
def addMethods():
    patch(FunctionType, 'partial', fn.partialmethod(fn.partial))
    patch(FunctionType, 'bind', fn.partialmethod(fn.partial))
    patch(BuiltinFunctionType, 'partial', fn.partialmethod(fn.partial))
    patch(BuiltinFunctionType, 'bind', fn.partialmethod(fn.partial))


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
