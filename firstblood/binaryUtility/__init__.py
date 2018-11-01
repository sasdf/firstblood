"""
Aim to build a uniform fronend to access capstone, keystone, binutils
make it ez to extend during CTF for special architecture

Implement the usage similar to pwnlib:
    util.disasm(b"\x55\x48\x8b\x05\xb8\x13\x00\x00", arch="i386")
    util.asm(b"INC ecx; DEC edx", arch="i386")

    or with curring:

    util.disasm(b"\x55\x48\x8b\x05\xb8\x13\x00\x00").i386
    util.asm(b"INC ecx; DEC edx").i386

DO NOT USE "shellcode".bytes, the unprintable bytes is different in b"shellcode"
Have to be implemented again here
"""



class archContext(object):
    arch = 'i386'
    archtectures = [
        'arm',
        'thumb',
        'arm64',
        'mips',
        'ppc',
        'ppc64',
        'sparc',
        'sysz',
        'i386',
        'amd64',
        'xcore'
    ]

    def setter(self, **kwargs):
        for k,v in kwargs.items():
            setattr(self,k,v)


def archWrap(func):
    @functools.wraps(func)
    def setter(*args, **kwargs):
        if not kwargs:
            return func(*args)

        archcontext.setter(**{k:kwargs.pop(k) for k,v in kwargs.copy().items() if hasattr(archContext,k)})

        return func(*args, **kwargs)
    return setter

archcontext = archContext()     #name context may collide with pwnlib

if __name__ == '__main__':
    from IPython import embed
    embed()