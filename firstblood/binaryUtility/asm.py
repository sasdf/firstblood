#from . import * for debug
from .Context import *
from capstone import *
from keystone import *

def lazyKeystone(arch, mode):
    def asm(code):
        ks = Ks(arch, mode)
        encoding = []

        encoding, count = ks.asm(code)

        return encoding
    return asm

asmDB = {
    'i386_l':     lazyKeystone(KS_ARCH_X86, KS_MODE_32),
    'amd64_l':    lazyKeystone(KS_ARCH_X86, KS_MODE_64),
    'arm_l':      lazyKeystone(KS_ARCH_ARM, KS_MODE_ARM),
    'arm_b':      lazyKeystone(KS_ARCH_ARM, KS_MODE_ARM+KS_MODE_BIG_ENDIAN),
    'thumb_l':    lazyKeystone(KS_ARCH_ARM, KS_MODE_THUMB),
    'thumb_b':    lazyKeystone(KS_ARCH_ARM, KS_MODE_THUMB+KS_MODE_BIG_ENDIAN),
    'arm64_l':    lazyKeystone(KS_ARCH_ARM64, KS_MODE_LITTLE_ENDIAN),
    'hexagon_l':  lazyKeystone(KS_ARCH_HEXAGON, KS_MODE_LITTLE_ENDIAN),
    'hexagon_b':  lazyKeystone(KS_ARCH_HEXAGON, KS_MODE_BIG_ENDIAN),
    'mips_l':     lazyKeystone(KS_ARCH_MIPS, KS_MODE_MIPS32),
    'mips_b':     lazyKeystone(KS_ARCH_MIPS, KS_MODE_MIPS32 + KS_MODE_BIG_ENDIAN),
    'mips64_l':   lazyKeystone(KS_ARCH_MIPS, KS_MODE_MIPS64),
    'mips64_b':   lazyKeystone(KS_ARCH_MIPS, KS_MODE_MIPS64 + KS_MODE_BIG_ENDIAN),
    'ppc_b':      lazyKeystone(KS_ARCH_PPC, KS_MODE_PPC32 + KS_MODE_BIG_ENDIAN),
    'ppc64_l':    lazyKeystone(KS_ARCH_PPC, KS_MODE_PPC64),
    'ppc64_b':    lazyKeystone(KS_ARCH_PPC, KS_MODE_PPC64 + KS_MODE_BIG_ENDIAN),
    'sparc_l':    lazyKeystone(KS_ARCH_SPARC, KS_MODE_SPARC32),
    'sparc_b':    lazyKeystone(KS_ARCH_SPARC, KS_MODE_SPARC32 + KS_MODE_BIG_ENDIAN),
    'sysz_b':     lazyKeystone(KS_ARCH_SYSTEMZ, KS_MODE_BIG_ENDIAN)
}

@archWrap
def asm(shellcode):
    """
    a cheap implementation
    need to optimize

    usage:
    asm('mov eax, 1', arch='i386')

    """
    assembler = asmDB.get(f"{context.arch}_{context.endian[0]}")
    if assembler is None:
        raise KeyError(f'No assembler for {context.arch} in {context.endian} endian')
    return assembler(shellcode)

@archWrap
def disasm(shellcode):
    pass


if __name__ == '__main__':
    def test(code, arch):
        print(f"{context.arch}_{context.endian} : {asm(code, arch=arch)}")

    test(b"add eax, ecx",'i386')
    test(b"add rax, rcx",'amd64')
    test(b"sub r1, r2, r5",'arm')
    test(b"movs r4, #0xf0","thumb")
    test(b"ldr w1, [sp, #0x8]",'arm64')
    test(b"and $9, $6, $7","mips")
    test(b"and $9, $6, $7","mips64")
    test(b"add 1, 2, 3","ppc64")
    test(b"add %g1, %g2, %g3","sparc")

    #test bigendian
    context.be

    test(b"sub r1, r2, r5",'arm')
    test(b"movs r4, #0xf0",'thumb')
    test( b"v23.w=vavg(v11.w,v2.w):rnd",'hexagon')
    test(b"and $9, $6, $7",'mips')
    test( b"and $9, $6, $7",'mips64')
    test(b"add 1, 2, 3",'ppc')
    test(b"add 1, 2, 3",'ppc64')
    test(b"add %g1, %g2, %g3",'sparc')
    test(b"a %r0, 4095(%r15,%r1)",'sysz')

    def test_curring(code):
        print(f"{context.arch}_{context.endian} : {asm(code)}")

    context.le 

    context.i386
    test(b"add eax, ecx",'i386')
    context.amd64
    test(b"add rax, rcx",'amd64')
    context.arm
    test(b"sub r1, r2, r5",'arm')
    context.thumb
    test(b"movs r4, #0xf0","thumb")
    context.arm64
    test(b"ldr w1, [sp, #0x8]",'arm64')
    context.mips
    test(b"and $9, $6, $7","mips")
    context.mips64
    test(b"and $9, $6, $7","mips64")
    context.ppc64
    test(b"add 1, 2, 3","ppc64")
    context.sparc
    test(b"add %g1, %g2, %g3","sparc")

    #test bigendian
    context.be
    context.arm
    test(b"sub r1, r2, r5",'arm')
    context.thumb
    test(b"movs r4, #0xf0",'thumb')
    context.hexagon
    test( b"v23.w=vavg(v11.w,v2.w):rnd",'hexagon')
    context.mips
    test(b"and $9, $6, $7",'mips')
    context.mips64
    test( b"and $9, $6, $7",'mips64')
    context.ppc
    test(b"add 1, 2, 3",'ppc')
    context.ppc64
    test(b"add 1, 2, 3",'ppc64')
    context.sparc
    test(b"add %g1, %g2, %g3",'sparc')
    context.sysz
    test(b"a %r0, 4095(%r15,%r1)",'sysz')

    from IPython import embed
    embed()