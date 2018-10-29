import itertools as it
import functools as fn

from collections import Counter
from collections import abc
from .patch import patch, needFlush
from .conv import conv
from .abc import getAllSubclasses


def last(func):
    @fn.wraps(func)
    def inner(self, *args, **kwargs):
        return func(*args, self, **kwargs)
    return inner


def wrapjoin(func, first=True, flatten=False):
    @fn.wraps(func)
    def inner(self, *args, **kwargs):
        if first:
            res = func(self, *args, **kwargs)
        else:
            res = func(*args, self, **kwargs)

        join = conv('', type(self))

        if flatten:
            res = join.join(res)
        else:
            res = (join.join(p) for p in res)
        return res
    return inner


def kwWrapper(func, typ, key):
    @fn.wraps(func)
    def inner(*args, **kwargs):
        if len(args) and isinstance(args[-1], typ):
            kwargs[key] = args[-1]
            args = args[:-1]
        return func(*args, **kwargs)
    return inner


def iterableJoinby(it, sep):
    return sep.join(conv(c, type(sep)) for c in it)


@fn.singledispatch
def xor(a, b):
    raise TypeError('Expected iterable')

@xor.register(str)
@xor.register(abc.ByteString)
def _(a, b):
    a = conv(a, bytes)
    b = conv(b, bytes)
    if len(a) > len(b):
        a, b = b, a
    return bytes(ai ^ bi for ai, bi in zip(it.cycle(a), b))

@xor.register(abc.Iterable)
def _(a: abc.Iterable, b):
    if not isinstance(b, abc.Iterable):
        b = [b]
    if len(a) > len(b):
        a, b = b, a
    return (ai ^ bi for ai, bi in zip(it.cycle(a), b))


reduceNone = []
def iterReduce(iterable, func, init=reduceNone):
    if init is reduceNone:
        return fn.reduce(func, iterable)
    else:
        return fn.reduce(func, iterable, init)


islice = fn.singledispatch(it.islice)

@islice.register(abc.Sequence)
def _(s: abc.Sequence, start, stop=None, step=1):
    if stop is None:
        start, stop = 0, start
    return s[start:stop:step]


def mean(iterable):
    return sum(iterable) / len(iterable)


def argmin(iterable):
    return min(zip(iterable, it.count()))[1]


def argmax(iterable):
    return max(zip(iterable, it.count()))[1]


def nchunks(iterable, n):
    if n <= 0:
        raise ZeroDivisionError('n should be positive')
    return chunk(iterable, len(iterable) // n)


@fn.singledispatch
def chunk(iterable, n):
    raise TypeError('Expected sequence or iterable')

@chunk.register(abc.Sequence)
def _(s, n):
    if n <= 0:
        raise ZeroDivisionError('n should be positive')
    return (s[i:i+n] for i in range(0, len(s), n))

@chunk.register(abc.Iterable)
def _(iterable, n):
    if n <= 0:
        raise ZeroDivisionError('n should be positive')
    iterable = iter(iterable)
    res = list(iterable.islice(n))
    while len(res):
        yield res
        res = list(iterable.islice(n))


rev = fn.singledispatch(reversed)
@rev.register(abc.Sequence)
def _(s):
    return s[::-1]


@needFlush
def addMethods():
    blacklist = ['_io', 'jedi.common.context']
    Strs = getAllSubclasses(abc.ByteString, blacklist)
    Strs.add(str)

    Sequences = getAllSubclasses(abc.Sequence, blacklist) # Reversible, Collection

    Iterables = getAllSubclasses(abc.Iterable, blacklist)

    Reversibles = getAllSubclasses(abc.Reversible, blacklist) # Iterable

    for t in Iterables - Strs:
        patch(t, 'chain', fn.partialmethod(it.chain))
        patch(t, 'compress', fn.partialmethod(it.compress))
        patch(t, 'dropwhile', last(it.dropwhile))
        patch(t, 'filter', last(filter))
        patch(t, 'filterfalse', last(it.filterfalse))
        patch(t, 'groupby', fn.partialmethod(it.groupby))
        patch(t, 'starmap', last(it.starmap))
        patch(t, 'takewhile', last(it.takewhile))
        patch(t, 'tee', fn.partialmethod(it.tee))
        patch(t, 'zip', zip)
        patch(t, 'zip_longest', fn.partialmethod(it.zip_longest))

        patch(t, 'product', kwWrapper(it.product, int, 'repeat'))
        patch(t, 'permutations', fn.partialmethod(it.permutations))
        patch(t, 'combinations', fn.partialmethod(it.combinations))
        patch(t, 'combinations_with_replacement',
            fn.partialmethod(it.combinations_with_replacement))

        patch(t, 'max', property(max))
        patch(t, 'min', property(min))
        patch(t, 'argmin', property(argmin))
        patch(t, 'argmax', property(argmax))
        patch(t, 'sum', property(sum))
        patch(t, 'mean', property(mean))
        patch(t, 'sorted', property(sorted))

    for t in Strs:
        patch(t, 'chain', wrapjoin(it.chain, flatten=True))
        patch(t, 'compress', wrapjoin(it.compress, flatten=True))
        patch(t, 'dropwhile', wrapjoin(it.dropwhile, first=False, flatten=True))
        patch(t, 'filter', wrapjoin(filter, first=False, flatten=True))
        patch(t, 'filterfalse', wrapjoin(it.filterfalse, first=False, flatten=True))
        patch(t, 'groupby', wrapjoin(it.groupby, flatten=False))
        patch(t, 'takewhile', wrapjoin(it.takewhile, first=False, flatten=True))
        patch(t, 'tee', wrapjoin(it.tee, flatten=False))
        patch(t, 'zip', wrapjoin(zip, flatten=False))
        patch(t, 'zip_longest', wrapjoin(it.zip_longest, flatten=False))

        patch(t, 'product', wrapjoin(kwWrapper(it.product, int, 'repeat'), flatten=False))
        patch(t, 'permutations', wrapjoin(it.permutations, flatten=False))
        patch(t, 'combinations', wrapjoin(it.combinations, flatten=False))
        patch(t, 'combinations_with_replacement',
            wrapjoin(it.combinations_with_replacement, flatten=False))

        patch(t, 'sorted', property(wrapjoin(sorted, flatten=True)))

    for t in Iterables:
        patch(t, 'accumulate', fn.partialmethod(it.accumulate))
        patch(t, 'cycle', property(it.cycle))
        patch(t, 'map', last(map))
        patch(t, 'reduce', iterReduce)
        patch(t, 'islice', islice)
        patch(t, 'take', islice)

        patch(t, 'uniq', property(set))
        patch(t, 'tuple', property(tuple))
        patch(t, 'list', property(list))
        patch(t, 'enum', property(enumerate))
        patch(t, 'iter', property(iter))
        patch(t, 'any', property(any))
        patch(t, 'all', property(all))
        patch(t, 'counter', property(Counter))
        patch(t, 'joinby', iterableJoinby)
        patch(t, 'chunk', chunk)

        patch(t, 'xor', xor)

    for t in Sequences:
        patch(t, 'nchunks', nchunks)

    for t in Reversibles:
        patch(t, 'rev', property(rev))


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
