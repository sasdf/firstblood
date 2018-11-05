import functools
from .asm import *

"""
Aim to build a uniform fronend to access capstone, keystone, binutils
make it ez to extend during CTF for special architecture

Implement the usage similar to pwnlib:

    util.disasm(b"\x55\x48\x8b\x05\xb8\x13\x00\x00", arch="i386")
    util.asm(b"INC ecx; DEC edx", arch="i386")

    or :

    context.i386
    util.disasm(b"\x55\x48\x8b\x05\xb8\x13\x00\x00")
    util.asm(b"INC ecx; DEC edx")

DO NOT USE "shellcode".bytes, the unprintable bytes is different in b"shellcode"
Have to be implemented again here
"""



if __name__ == '__main__':
    from IPython import embed
    embed()