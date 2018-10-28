import hashlib
from .conv import conv
from .patch import patch, needFlush


def _bytesdigest(algo):
    def digest(s):
        return algo(conv(s, bytes)).digest()
    return digest


blake2b = _bytesdigest(hashlib.blake2b)
blake2s = _bytesdigest(hashlib.blake2s)
md5 = _bytesdigest(hashlib.md5)
sha1 = _bytesdigest(hashlib.sha1)
sha224 = _bytesdigest(hashlib.sha224)
sha256 = _bytesdigest(hashlib.sha256)
sha384 = _bytesdigest(hashlib.sha384)
sha512 = _bytesdigest(hashlib.sha512)
sha3_224 = _bytesdigest(hashlib.sha3_224)
sha3_256 = _bytesdigest(hashlib.sha3_256)
sha3_384 = _bytesdigest(hashlib.sha3_384)
sha3_512 = _bytesdigest(hashlib.sha3_512)


@needFlush
def addMethods():
    patch(bytes, 'blake2b', property(blake2b))
    patch(bytes, 'blake2s', property(blake2s))
    patch(bytes, 'md5', property(md5))
    patch(bytes, 'sha1', property(sha1))
    patch(bytes, 'sha224', property(sha224))
    patch(bytes, 'sha256', property(sha256))
    patch(bytes, 'sha384', property(sha384))
    patch(bytes, 'sha512', property(sha512))
    patch(bytes, 'sha3_224', property(sha3_224))
    patch(bytes, 'sha3_256', property(sha3_256))
    patch(bytes, 'sha3_384', property(sha3_384))
    patch(bytes, 'sha3_512', property(sha3_512))

    patch(str, 'blake2b', property(blake2b))
    patch(str, 'blake2s', property(blake2s))
    patch(str, 'md5', property(md5))
    patch(str, 'sha1', property(sha1))
    patch(str, 'sha224', property(sha224))
    patch(str, 'sha256', property(sha256))
    patch(str, 'sha384', property(sha384))
    patch(str, 'sha512', property(sha512))
    patch(str, 'sha3_224', property(sha3_224))
    patch(str, 'sha3_256', property(sha3_256))
    patch(str, 'sha3_384', property(sha3_384))
    patch(str, 'sha3_512', property(sha3_512))


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
