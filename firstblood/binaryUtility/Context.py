import functools

class archContext(object):
    arch = 'i386'
    endian = 'little'

    def setter(self, **kwargs):
        for k,v in kwargs.items():
            setattr(self,k,v)

    def _little(self):
        self.endian = "little"
    def _big(self):
        self.endian = "big"
    def _setArch(self, arch):
        self.arch = arch
    #set endian 
    little = property(_little)
    le = property(_little)
    big = property(_big)
    be = property(_big)
    #set arch
    amd64 = property(functools.partial(_setArch,arch='amd64'))
    arm = property(functools.partial(_setArch,arch='arm'))
    arm64 = property(functools.partial(_setArch,arch='arm64'))
    hexagon = property(functools.partial(_setArch,arch='hexagon'))
    i386 = property(functools.partial(_setArch,arch='i386'))
    mips = property(functools.partial(_setArch,arch='mips'))
    mips64 = property(functools.partial(_setArch,arch='mips64'))
    ppc = property(functools.partial(_setArch,arch='ppc'))
    ppc64 = property(functools.partial(_setArch,arch='ppc64'))
    sparc = property(functools.partial(_setArch,arch='sparc'))
    sysz = property(functools.partial(_setArch,arch='sysz'))
    thumb = property(functools.partial(_setArch,arch='thumb'))

def archWrap(func):
    @functools.wraps(func)
    def setter(*args, **kwargs):
        if not kwargs:
            return func(*args)

        context.setter(**{k:kwargs.pop(k) for k,v in kwargs.copy().items() if hasattr(archContext,k)})

        return func(*args, **kwargs)
    return setter


context = archContext()     #name context may collide with pwnlib