# FirstBlood

> I'm not writing production scripts, I just want to get the firstblood.

This is a python 3 library which will add some method to builtin objects,
and provide some useful utilities.

It's still WIP and needs a lot of refactoring.

WARNING: THIS LIBRARY MAY CHANGE THE BEHAVIOR OF PYTHON,
WHICH SHOULD NOT BE USED IN PRODUCTION ENVIRONMENT.


## TOC
* Bytes, String and Hash
* Method Chaining
* Iterable
* Function
* Integer and Modulo
* Object
* JSON
* Type Conversion
* Unified I/O


## Get Started
```python
from firstblood.all import *
```


## Get Started - Bytes, String and Hash
Python 3 has many great features,
but it's not very suitable for CTF due to the seperation of str and bytes.
The concept of bytes is really useful,
you should follow it to handle encoding correctly in production.
But it is annoying when you have a tight deadline (e.g. during the CTF).

Take base64 encoding for an example,
here how it looks like in python 2:
```python
str_var.encode('base64')
```
in python 3:
```python
import binascii
binascii.b2a_base64(str_var.encode('utf8')).decode('utf8')
```
With this library, you can write:
```python
str_var.b64e
# or
str_var.base64e
# or
str_var.enc('base64')
```

We also have a `xor` method which is very useful for crypto tasks:
```python
>>> 'abc'.xor('cde')
b'\x02\x06\x06'
>>> 'abc'.xor(32)
b'ABC'
```

To convert between bytes, str and int:
```python
>>> 'abc'.bytes
b'abc'
>>> 'abc'.bytes.str
'abc'
>>> 'a'.ord          # ord
97
>>> b'1337'.int10    # decimal
1337
>>> b'1337'.int16    # hex
4919
>>> b'\x39\x05'.int  # little endian
1337
>>> b'\x05\x39'.Int  # big endian
1337
>>> b'\x39\x05'.u16  # integer modulo ring
(1337 mod 2^16)
```

We also bind hashlib digest to str and bytes:
```python
>>> 'abc'.sha1
b'\xa9\x99>6G\x06\x81j\xba>%qxP\xc2l\x9c\xd0\xd8\x9d'
>>> 'abc'.sha1.hexe
'a9993e364706816aba3e25717850c26c9cd0d89d'
>>> 'abc'.blake2s
b'P\x8c^\x8c2|\x14\xe2\xe1\xa7+\xa3N\xebE/7E\x8b \x9e\xd6:)M\x99\x9bL\x86gY\x82'
>>> 'abc'.blake2s.hexe
'508c5e8c327c14e2e1a72ba34eeb452f37458b209ed63a294d999b4c86675982'
```


## Get Started - Method Chaining
The nature of python is nesting function call:
```python
len(listA)
# or
list(map(str, listA))
# or
enumerate(zip(listA, listB))
# or
b2a_base64(sha1(a2b_base64(str_var)).digest()).decode('utf8')
```
But I'm a big fan of method chaining like what we do in Javascript.
With this library, we can write:
```python
listA.len
# or
listA.map(str).list
# or
listA.zip(listB).enum
# or
str_var.b64d.sha1.b64e
```
The order of method is same as the order of execution.
Much better, right :)


## Get Started - Iterable and Function
We intergrate builtin functions and a powerful module, itertools,
to iterables itself.

If we want to bruteforce length 3 pairs of a given set:
```python
>>> range(2).product(3).take(5).list
[(0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), (1, 0, 0)]
>>> 'ab'.product(3).take(5).list
['aaa', 'aab', 'aba', 'abb', 'baa']
```

And some useful utilities for processing iterables:
```python
>>> 'abcabc'.rev
'cbacba'
>>> 'abcabc'.sorted
'aabbcc'
>>> 'abcabc'.chunk(2).list
['ab', 'ca', 'bc']
>>> 'abcabc'.nchunks(2).list
['abc', 'abc']
>>> range(4).xor(32).list
[32, 33, 34, 35]
```

We also add some numpy-like functions:
```python
>>> range(5, 10).sum
35
>>> range(5, 10).mean
7.0
>>> range(5, 10).min
5
>>> range(5, 10).argmin
0
>>> range(5, 10).max
9
>>> range(5, 10).argmax
4
>>> range(10).all
False
>>> range(10).any
True
>>>
```

Convert between different iterables is very easy:
```python
>>> 'abcabc'.list     # list
['a', 'b', 'c', 'a', 'b', 'c']
>>> 'abcabc'.uniq     # set
{'a', 'b', 'c'}
>>> 'abcabc'.tuple    # tuple
('a', 'b', 'c', 'a', 'b', 'c')
>>> 'abcabc'.counter  # collections.Counter
Counter({'a': 2, 'b': 2, 'c': 2})
>>> 'abcabc'.list.joinby(', ')
'a, b, c, a, b, c'
>>> 'abcabc'.list.joinby(b', ')
b'a, b, c, a, b, c'
```


## Get Started - Function
Similar to itertools, we have functools for functions,
we bind `partial` method on it:
```python
>>> (lambda x: x).partial(10)()
10
>>> (lambda x: x).bind(10)()
10
```

#### TODO
compose


## Get Started - Integer and Modulo
We provide different ways to convert to hex and bin:
```python
>>> (1337).hex
'0539'
>>> (1337).bin
'0000010100111001'
```
where `hex` is aligned to two chars and `bin` is aligned to 8 chars.

We have a special module for calculation modulo arithmetic:
```python
>>> (13).u16
(13 mod 2^16)
>>> (13).u16 << 15
(32768 mod 2^16)
>>> (13).u16 << 16
(0 mod 2^16)

>>> (13).mod(100) * 10
(30 mod 100)
>>> (13).mod(100) / 3
(71 mod 100)
>>> (71).mod(100) * 3
(13 mod 100)
>>> 1 / (13).mod(100)
(77 mod 100)
>>> (13).mod(100).inv
(77 mod 100)
```

Some utilities:
```python
>>> (30).align(8)
32
>>> (32).align(8)
32
>>> (30).bin
'00011110'
>>> (30).mask(4).bin
'00010000'
```

To convert between int, bytes and str:
```python
>>> (97).chr
'a'
>>> (1952802156).str
'1952802156'
>>> (1952802156).bytes
b'leet'
>>> (1952802156).p32
b'leet'
>>> (1952802156).p64
b'leet\x00\x00\x00\x00'
```


## Get Started - Object
We bind some builtin functions to Object:
```python
>>> str.dir.take(5).list
['Int', '__add__', '__class__', '__contains__', '__delattr__']
>>> str.hasattr('__name__')
True
>>> str.getattr('__name__')
'str'
>>> str.setattr('__name__', 'error')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: cant set attributes of built-in/extension type 'str'
```


## Get Started - JSON
Converting between data and JSON string can be done with attributes:
```python
>>> 'abc'.json
'"abc"'
>>> (1337).json
'1337'
>>> {'a': 1}.json
'{"a": 1}'
>>> {'a': 1}.json.jsond
{'a': 1}
```


## Get Started - Type conversion
TBD

Binding codecs module to attribute.
```python
str_var.enc(encoding)
str_var.dec(encoding)
```


## Get Started - Unified I/O
TBD

Inspired by the awesome interface of pwntools,
we provide a unified interface for communicating between proceess, network, or even files.
```python
r.line([size, keep=False])  # read a line up to size bytes. alias of r.readline([size])
r.line(data)  # alias of r.writeline(data)
r.lines([hint, keep=False]) # read all lines up to hint bytes. alias of r.readlines([hint])
r.until('input: ', [keep=False, drop=True]) # alias of r.readuntil('input: ')
r.read([n]) # read up to n bytes
r.peek([n]) # peek up to n bytes
r.write(data) # write data
r.seek(n) # file only
```
Moreover, we make it chainable to provide a cleaner interface.
```python
r.after('input: ').line(data).read(5)
r.before('0x').line()
```

We also provide shortcuts to files to avoid `with open` block:
```python
data = uio.read('/path/to/file') # r mode
data = uio.readbin('/path/to/file') # rb mode
data = uio.readline('/path/to/file') # r mode
data = uio.readbinline('/path/to/file') # rb mode
data = uio.readlines('/path/to/file') # r mode
data = uio.readbinlines('/path/to/file') # rb mode
data = uio.readuntil('/path/to/file', 'end') # r mode
data = uio.readbinuntil('/path/to/file', b'end') # r mode
data = uio.write('/path/to/file', data) # r mode
data = uio.writebin('/path/to/file', data) # r mode
data = uio.writeline('/path/to/file', data) # r mode
data = uio.writebinline('/path/to/file', data) # r mode
data = uio.writelines('/path/to/file', lines) # r mode
data = uio.writebinlines('/path/to/file', lines) # r mode
```
[Future] Maybe we can bind uio and pathlib to str attributes?
```python
data = '/path/to/file'.read()
data = '/path/to/file'.readbin()
data = '/path/to/file'.readlines()
data = '/path/to/file'.write(data)

f = '/path/to/file'.open()
files = '/path/to/dir'.iterdir()
```


## API
TBD

The project is still working in progress,
we does'nt has any stable api now.


## Current Limitation
Overriding operators of builtin type cannot be done in pure python,
those types save C function pointers directly.
