import codecs
import json
from collections import namedtuple
from .patch import patch, needFlush


def identity(self, *args, **kwargs):
    """Do nothing"""
    return self


def bytes2str(inp):
    """Decode bytes to str with default encoding"""
    return inp.decode('utf8')


def str2bytes(inp):
    """Encode str to bytes with default encoding"""
    return inp.encode('utf8')


def singleline(inp):
    """Join everything to a single line"""
    return inp.replace('\n', '')


def x2bytes(x):
    return str(x).encode('utf8')


# {from}_{to}, where * represents wildcard
convDB = {
    'bytes_str': bytes2str,
    'str_bytes': str2bytes,
    '*_bytes': x2bytes,
}


def conv(self, typ):
    """Convert self to `typ` type"""

    # Identity
    if isinstance(self, typ):
        return self

    # Lookup for registered conversion
    trans = f'{type(self).__name__}_{typ.__name__}'
    trans = convDB.get(trans)
    if trans is not None:
        return trans(self)

    # Lookup for registered fallback
    trans = f'*_{typ.__name__}'
    trans = convDB.get(trans)
    if trans is not None:
        return trans(self)

    # Direct conversion fallback
    return typ(self)


CodecsIOFmt = namedtuple('CodecsIOFmt',
    ['src', 'dst', 'func', 'inhook', 'prehook', 'posthook', 'outhook'],
    defaults=(None, None, None, identity, identity, identity, identity)
    )

codecsDB = {
    'base64_enc': CodecsIOFmt(bytes, str, outhook=singleline),
    'base64_dec': CodecsIOFmt(bytes, bytes),
    'hex_enc': CodecsIOFmt(bytes, str),
    'hex_dec': CodecsIOFmt(bytes, bytes),
    'utf8_enc': CodecsIOFmt(str, bytes),
    'utf8_dec': CodecsIOFmt(bytes, str),
    'ascii_enc': CodecsIOFmt(str, bytes),
    'ascii_dec': CodecsIOFmt(bytes, str),
    'json_dec': CodecsIOFmt(str, None, func=json.loads),
}


def _runconv(postfix, func):
    def runconv(s, encoding, *args, **kwargs):
        iofmt = codecsDB.get(encoding + postfix)
        if iofmt is None:
            raise KeyError('Encoding not found')
        s = iofmt.inhook(s)
        if iofmt.dst is not None:
            s = conv(s, iofmt.src)
        s = iofmt.prehook(s)
        if iofmt.func is not None:
            s = iofmt.func(s)
        else:
            s = func(s, encoding, *args, **kwargs)
        s = iofmt.posthook(s)
        if iofmt.dst is not None:
            s = conv(s, iofmt.dst)
        s = iofmt.outhook(s)
        return s
    return runconv


convenc = _runconv('_enc', codecs.encode)
convdec = _runconv('_dec', codecs.decode)


@needFlush
def addMethods():
    patch(str, 'enc', convenc)
    patch(str, 'dec', convdec)
    patch(bytes, 'enc', convenc)
    patch(bytes, 'dec', convdec)


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
