import functools as fn
import struct
from .conv import identity, bytes2str, convenc, convdec, convDB
from .patch import patch, needFlush
from ..modulo import GF2_8, GF2_16, GF2_32, GF2_64


convDB['bytes_int'] = fn.partial(int.from_bytes, byteorder='little')


def bytesord(s):
    if len(s) != 1:
        raise TypeError(f'ord() expected a character, but string of length {len(s)} found')
    return s[0]


def unpackWrapper(fmt, Ring):
    def inner(self):
        return Ring(struct.unpack(fmt, self)[0])
    return inner


@needFlush
def addMethods():
    patch(bytes, 'bytes', property(identity))
    patch(bytes, 'str', property(bytes2str))
    patch(bytes, 'ord', property(bytesord))
    patch(bytes, 'ords', property(list))
    patch(bytes, 'u8', property(unpackWrapper('<B', GF2_8)))
    patch(bytes, 'u16', property(unpackWrapper('<H', GF2_16)))
    patch(bytes, 'U16', property(unpackWrapper('>H', GF2_16)))
    patch(bytes, 'u32', property(unpackWrapper('<I', GF2_32)))
    patch(bytes, 'U32', property(unpackWrapper('>I', GF2_32)))
    patch(bytes, 'u64', property(unpackWrapper('<Q', GF2_64)))
    patch(bytes, 'U64', property(unpackWrapper('>Q', GF2_64)))

    patch(bytes, 'ascii', property(fn.partial(convdec, encoding='ascii')))

    patch(bytes, 'hexe', property(fn.partial(convenc, encoding='hex')))
    patch(bytes, 'hexd', property(fn.partial(convdec, encoding='hex')))

    patch(bytes, 'base64e', property(fn.partial(convenc, encoding='base64')))
    patch(bytes, 'b64e', property(fn.partial(convenc, encoding='base64')))
    patch(bytes, 'base64d', property(fn.partial(convdec, encoding='base64')))
    patch(bytes, 'b64d', property(fn.partial(convdec, encoding='base64')))

    patch(bytes, 'jsond', property(fn.partial(convdec, encoding='json')))

    patch(bytes, 'int', property(fn.partial(int.from_bytes, byteorder='little')))
    patch(bytes, 'Int', property(fn.partial(int.from_bytes, byteorder='big')))
    patch(bytes, 'int2', property(fn.partial(int, base=2)))
    patch(bytes, 'int10', property(fn.partial(int, base=10)))
    patch(bytes, 'int16', property(fn.partial(int, base=16)))


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
