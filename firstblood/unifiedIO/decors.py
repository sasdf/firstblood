import io


def _chainable(funcname):
    def transformer(cls):
        func = getattr(cls, funcname)
        def inner(self, *args, **kwargs):
            func(self, *args, **kwargs)
            return self
        inner.__name__ = funcname
        inner.__qualname__ = f'{cls.__name__}.{funcname}'
        setattr(cls, funcname, inner)
        return cls
    return transformer


def _virtual(attrname, prop=False):
    def transformer(cls):
        if hasattr(cls, attrname):
            return cls
        def inner(self, *args, **kwargs):
            raise io.UnsupportedOperation()
        inner.__virtual__ = True
        inner.__name__ = attrname
        inner.__qualname__ = f'{cls.__name__}.{attrname}'
        setattr(cls, attrname, property(inner) if prop else inner)
        return cls
    return transformer


def _weakalias(attrname, funcname=None, prop=False):
    if funcname is None:
        funcname = '_' + attrname

    def transformer(cls):
        if hasattr(cls, attrname):
            return cls
        def inner(self, *args, **kwargs):
            func = getattr(self, funcname)
            return func if prop else func(self, *args, **kwargs)
        inner.__name__ = attrname
        inner.__qualname__ = f'{cls.__name__}.{attrname}'
        setattr(cls, attrname, property(inner) if prop else inner)
        return cls
    return transformer


def _raw(attrname, funcname=None, prop=False):
    if funcname is None:
        funcname = attrname.lstrip('_')

    def transformer(cls):
        def inner(self, *args, **kwargs):
            try:
                func = getattr(self.raw, funcname)
            except AttributeError:
                func = getattr(super(cls, self), attrname)
            return func if prop else func(*args, **kwargs)
        inner.__name__ = attrname
        inner.__qualname__ = f'{cls.__name__}.{attrname}'
        setattr(cls, attrname, property(inner) if prop else inner)
        return cls
    return transformer
