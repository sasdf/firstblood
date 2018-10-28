# Modified from https://gist.github.com/bricef/1b0389ee89bd5b55113c7f3f3d6394ae
# Found this from Armin R. on Twitter, what a beautiful gem ;)

import ctypes
import functools as fn
from types import MappingProxyType


##-- Figure out the size of size_t type --##
if hasattr(ctypes.pythonapi, 'Py_InitModule4_64'):
    _Py_ssize_t = ctypes.c_int64
else:
    _Py_ssize_t = ctypes.c_int


##-- Define PyObject type --##
# regular python
class _PyObject(ctypes.Structure):
    pass
_PyObject._fields_ = [
    ('ob_refcnt', _Py_ssize_t),
    ('ob_type', ctypes.POINTER(_PyObject))
]

# python with trace
if object.__basicsize__ != ctypes.sizeof(_PyObject):
    class _PyObject(ctypes.Structure):
        pass
    _PyObject._fields_ = [
        ('_ob_next', ctypes.POINTER(_PyObject)),
        ('_ob_prev', ctypes.POINTER(_PyObject)),
        ('ob_refcnt', _Py_ssize_t),
        ('ob_type', ctypes.POINTER(_PyObject))
    ]


class _DictProxy(_PyObject):
    """Proxy for casting _PyObject back to object"""
    _fields_ = [('dict', ctypes.POINTER(_PyObject))]


pendingFlush = False
def needFlush(func):
    """Decorator for handling flush keyword argument"""
    @fn.wraps(func)
    def inner(*args, flush=None, **kwargs):
        global pendingFlush
        removePending = False
        if flush is None and not pendingFlush:
            flush = pendingFlush = removePending = True
        res = func(*args, **kwargs)
        if flush:
            ctypes.pythonapi.PyType_ClearCache()
        if removePending:
            pendingFlush = False
        return res
    return inner


def reveal_dict(proxy):
    """
    Get the underlying dict from MappingProxyType
    and force convert to python dict
    """
    if not isinstance(proxy, MappingProxyType):
        raise TypeError('dictproxy expected')
    dp = _DictProxy.from_address(id(proxy))
    ns = {}
    ctypes.pythonapi.PyDict_SetItem(ctypes.py_object(ns),
                                    ctypes.py_object(None),
                                    dp.dict)
    return ns[None]


def get_class_dict(cls):
    """Get the dict and convert the type if it's MappingProxyType"""
    d = getattr(cls, '__dict__', None)
    if d is None:
        raise TypeError('given class does not have a dictionary')
    if isinstance(d, MappingProxyType):
        return reveal_dict(d)
    return d


@needFlush
def patch(cls, key, value, override=None):
    """Monkey patch for both custom and builtin types"""
    if not isinstance(cls, type):
        raise TypeError('Not a type')
    if hasattr(cls, key):
        if override is None:
            raise KeyError(f'Unexpected Override: {cls}[{key}]')
        elif override is False:
            return False
    try:
        setattr(cls, key, value)
    except TypeError:
        d = get_class_dict(cls)
        d[key] = value
    return True


if __name__ == '__main__':
    class cls():
        def foo(self):
            return 'no'
    patch(cls, 'foo', lambda x: 'bar', override=True)
    if cls().foo() == 'bar':
        print('[+] Patch normal class success')

    patch(str, 'lower', lambda x: 'bar', override=True)
    if 'test'.lower() == 'bar':
        print("[+] Patch builtin class success")
