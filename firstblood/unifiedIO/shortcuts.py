from .file import UnifiedFile


def _shortcut(funcname, mode, ret):
    def inner(path, *args, **kwargs):
        with UnifiedFile.open(path, mode) as f:
            res = getattr(f, funcname)(*args, **kwargs)
            if ret: return res
    inner.__name__ = funcname
    inner.__qualname__ = funcname
    return inner


read           = _shortcut('read',       'r',  True)
readaline      = _shortcut('readline',   'r',  True) # avoid name collision of module readline
readlines      = _shortcut('readlines',  'r',  True)
readuntil      = _shortcut('readuntil',  'r',  True)
write          = _shortcut('write',      'w',  False)
writeline      = _shortcut('writeline',  'w',  False)
writelines     = _shortcut('writelines', 'w',  False)
append         = _shortcut('write',      'a',  False)
appendline     = _shortcut('writeline',  'a',  False)
appendlines    = _shortcut('writelines', 'a',  False)

readbin        = _shortcut('read',       'rb', True)
readbinline    = _shortcut('readline',   'rb', True)
readbinlines   = _shortcut('readlines',  'rb', True)
readbinuntil   = _shortcut('readuntil',  'rb', True)
writebin       = _shortcut('write',      'wb', False)
writebinline   = _shortcut('writeline',  'wb', False)
writebinlines  = _shortcut('writelines', 'wb', False)
appendbin      = _shortcut('write',      'ab', False)
appendbinline  = _shortcut('writeline',  'ab', False)
appendbinlines = _shortcut('writelines', 'ab', False)
