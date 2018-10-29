import numbers
import math
import functools as fn
from libnum import invmod


def funcWrapper(func):
    def inner(self, other):
        if isinstance(other, Mod):
            if other.modulo != self.modulo:
                raise ValueError('Operation between different integer ring')
            other = other.num
        res = func(self, other)
        if not isinstance(res, Mod):
            res = Mod(res, self.modulo)
        return res
    return inner


def cmpWrapper(func):
    def inner(self, other):
        if isinstance(other, Mod):
            if other.modulo != self.modulo:
                raise ValueError('Operation between different integer ring')
            other = other.num
        return getattr(self.num, func)(other)
    return inner


def rawUnaryWrapper(func):
    def inner(self):
        return getattr(self.num, func)()
    return inner


def unaryWrapper(func):
    def inner(self):
        return Mod(getattr(self.num, func)(), self.modulo)
    return inner


def binaryWrapper(func):
    def inner(self, other):
        if isinstance(other, Mod):
            if other.modulo != self.modulo:
                raise ValueError('Operation between different integer ring')
            other = other.num
        return Mod(getattr(self.num, func)(other), self.modulo)
    return inner


def identity(self):
    return self


class Mod(numbers.Integral):
    def __init__(self, num, modulo, modexpr=None):
        assert(modulo > 0 and int(modulo) == modulo)
        modulo = int(modulo)
        self.num = num % modulo
        self.modulo = modulo
        if modexpr is not None:
            self.modexpr = modexpr
        else:
            exp2 = round(math.log2(modulo))
            diff = modulo - (1 << exp2)
            if diff == 0 and exp2 > 9:
                self.modexpr = f'2^{exp2}'
            elif diff == 1 and exp2 > 9:
                self.modexpr = f'2^{exp2} + 1'
            elif diff == -1 and exp2 > 9:
                self.modexpr = f'2^{exp2} - 1'
            else:
                self.modexpr = str(modulo)

    __lt__ = cmpWrapper('__lt__')
    __le__ = cmpWrapper('__le__')
    __eq__ = cmpWrapper('__eq__')
    __ne__ = cmpWrapper('__ne__')
    __gt__ = cmpWrapper('__gt__')
    __ge__ = cmpWrapper('__ge__')

    __bool__ = rawUnaryWrapper('__bool__')

    __abs__    = unaryWrapper('__abs__')
    __neg__    = unaryWrapper('__neg__')
    __invert__ = unaryWrapper('__invert__')

    __ceil__  = identity
    __floor__ = identity
    __pos__   = identity
    __round__ = identity
    __trunc__ = identity

    __add__      = binaryWrapper('__add__')
    __sub__      = binaryWrapper('__sub__')
    __mul__      = binaryWrapper('__mul__')
    __floordiv__ = binaryWrapper('__floordiv__')
    __lshift__   = binaryWrapper('__lshift__')
    __rshift__   = binaryWrapper('__rshift__')
    __and__      = binaryWrapper('__and__')
    __xor__      = binaryWrapper('__xor__')
    __or__       = binaryWrapper('__or__')

    __radd__      = binaryWrapper('__radd__')
    __rsub__      = binaryWrapper('__rsub__')
    __rmul__      = binaryWrapper('__rmul__')
    __rfloordiv__ = binaryWrapper('__rfloordiv__')
    __rlshift__   = binaryWrapper('__rlshift__')
    __rrshift__   = binaryWrapper('__rrshift__')
    __rand__      = binaryWrapper('__rand__')
    __rxor__      = binaryWrapper('__rxor__')
    __ror__       = binaryWrapper('__ror__')


    @funcWrapper
    def __pow__(self, other):
        return pow(self.num, other, self.modulo)

    @funcWrapper
    def __truediv__(self, other):
        return self * invmod(other, self.modulo)

    @property
    def inv(self):
        return Mod(invmod(self.num, self.modulo), self.modulo)

    @funcWrapper
    def __mod__(self, other):
        return Mod(self.num, other)

    def mod(self, other):
        return self % other


    @funcWrapper
    def __rpow__(self, other):
        return pow(other, self.num, self.modulo)

    @funcWrapper
    def __rtruediv__(self, other):
        return other * invmod(self.num, self.modulo)

    @funcWrapper
    def __rmod__(self, other):
        return Mod(other, self.num)

    @property
    def int(self):
        return self.num

    def __int__(self):
        return self.num

    def __hash__(self):
        return hash(self.num)

    def __repr__(self):
        return f'({self.num} mod {self.modexpr})'


GF2_64 = fn.partial(Mod, modulo=2**64)
GF2_32 = fn.partial(Mod, modulo=2**32)
GF2_16 = fn.partial(Mod, modulo=2**16)
GF2_8 = fn.partial(Mod, modulo=2**8)

if __name__ == '__main__':
    from IPython import embed
    embed()
