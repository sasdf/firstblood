import functools as fn
from .conv import identity, str2bytes, convenc, convdec, convDB
from .patch import patch, needFlush


def str2bint(self, byteorder):
    """Convert large int string to number"""
    return int.from_bytes(self.encode('utf8'), byteorder=byteorder)


def strIsAscii(self):
    """Make sure all chars are ascii"""
    self.encode('ascii')
    return self
convDB['str_int'] = fn.partial(int, base=10)


def strords(s):
    return (ord(c) for c in s)


@needFlush
def addMethods():
    patch(str, 'bytes', property(str2bytes))
    patch(str, 'str', property(identity))
    patch(str, 'ascii', property(strIsAscii))
    patch(str, 'ord', property(ord))
    patch(str, 'ords', property(strords))

    patch(str, 'hexe', property(fn.partial(convenc, encoding='hex')))
    patch(str, 'hexd', property(fn.partial(convdec, encoding='hex')))

    patch(str, 'base64e', property(fn.partial(convenc, encoding='base64')))
    patch(str, 'b64e', property(fn.partial(convenc, encoding='base64')))
    patch(str, 'base64d', property(fn.partial(convdec, encoding='base64')))
    patch(str, 'b64d', property(fn.partial(convdec, encoding='base64')))

    patch(str, 'jsond', property(fn.partial(convdec, encoding='json')))

    patch(str, 'int', property(fn.partial(str2bint, byteorder='little')))
    patch(str, 'Int', property(fn.partial(str2bint, byteorder='big')))
    patch(str, 'int2', property(fn.partial(int, base=2)))
    patch(str, 'int10', property(fn.partial(int, base=10)))
    patch(str, 'int16', property(fn.partial(int, base=16)))


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
