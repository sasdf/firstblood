import math
import struct
import functools as fn
from .patch import patch, needFlush
from .conv import convDB
from ..modulo import Mod, GF2_8, GF2_16, GF2_32, GF2_64


def intAlign(self, size):
    """Align the number to the smallest number of multiple `size`"""
    return self + (-self % size)


def alignStr(x, size, pad=' ', padzero=True):
    """Pad length of `x` to multiple of `size`"""
    if len(x) == 0:
        return pad * size if padzero else x
    x = pad * (-len(x) % size) + x
    return x


def int2hex(self):
    """Convert integer to %02x hex strings"""
    res = alignStr('%x' % abs(self), 2, '0')
    if self < 0:
        res = '-' + res
    return res


def int2bin(self):
    """Convert integer to %08b binary strings"""
    res = alignStr(bin(abs(self))[2:], 8, '0')
    if self < 0:
        res = '-' + res
    return res


def intByteSize(self):
    """Return the smallest size of bytes that can hold the integer"""
    return math.ceil(self.bit_length() / 8)


def int2bytes(self):
    """Encode the integer to little endian bytes"""
    return self.to_bytes(intByteSize(self), 'little')
convDB['int_bytes'] = int2bytes
convDB['int_str'] = str


def int2Bytes(self):
    """Encode the integer to big endian bytes"""
    return self.to_bytes(intByteSize(self), 'big')


def intMask(self, mask):
    """Mask out lower `mask` bits"""
    return self & ~((1 << mask) - 1)


def packWrapper(fmt, Ring):
    def inner(self):
        return struct.pack(fmt, self)
    return inner


@needFlush
def addMethods():
    patch(int, 'str', property(str))
    patch(int, 'chr', property(chr))
    patch(int, 'u8', property(GF2_8))
    patch(int, 'u16', property(GF2_16))
    patch(int, 'u32', property(GF2_32))
    patch(int, 'u64', property(GF2_64))
    patch(int, 'mod', lambda x, n: Mod(x, n))
    patch(int, 'p8', property(fn.partial(struct.pack, '<B')))
    patch(int, 'p16', property(fn.partial(struct.pack, '<H')))
    patch(int, 'P16', property(fn.partial(struct.pack, '>H')))
    patch(int, 'p32', property(fn.partial(struct.pack, '<I')))
    patch(int, 'P32', property(fn.partial(struct.pack, '>I')))
    patch(int, 'p64', property(fn.partial(struct.pack, '<Q')))
    patch(int, 'P64', property(fn.partial(struct.pack, '>Q')))

    patch(int, 'hex', property(int2hex))
    patch(int, 'bin', property(int2bin))
    patch(int, 'align', intAlign)
    patch(int, 'mask', intMask)

    patch(int, 'bytes', property(int2bytes))
    patch(int, 'Bytes', property(int2Bytes))

    patch(int, 'byte_length', intByteSize)


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
