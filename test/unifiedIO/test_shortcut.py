import unittest
import tempfile
import os
from pathlib import Path

from firstblood import uio


dataFolder = Path(__file__).parent / 'data'


class TestLines_shortcut(unittest.TestCase):

    def read(self):
        with open(self.path) as f:
            return f.read()

    def readbin(self):
        with open(self.path, 'rb') as f:
            return f.read()

    def setUp(self):
        fd, self.path = tempfile.mkstemp(prefix='uiotest-')
        os.close(fd)
        self.linestxt =  dataFolder / 'lines.txt'
        
    def tearDown(self):
        os.unlink(self.path)

    def test_read(self):
        data = uio.read(self.linestxt)
        self.assertEqual(data, 'first line\nsecond line\nthird line\nend\n')

    def test_readbin(self):
        data = uio.readbin(self.linestxt)
        self.assertEqual(data, b'first line\nsecond line\nthird line\nend\n')

    def test_readn(self):
        data = uio.read(self.linestxt, 20)
        self.assertEqual(data, 'first line\nsecond li')

    def test_readbinn(self):
        data = uio.readbin(self.linestxt, 20)
        self.assertEqual(data, b'first line\nsecond li')
        
    def test_lines(self):
        data = uio.readlines(self.linestxt)
        self.assertEqual(data, [
            'first line',
            'second line',
            'third line',
            'end',
            ])

    def test_binlines(self):
        data = uio.readbinlines(self.linestxt)
        self.assertEqual(data, [
            b'first line',
            b'second line',
            b'third line',
            b'end',
            ])

    def test_lines_keep(self):
        data = uio.readlines(self.linestxt, keep=True)
        self.assertEqual(data, [
            'first line\n',
            'second line\n',
            'third line\n',
            'end\n',
            ])
            
    def test_binlines_keep(self):
        data = uio.readbinlines(self.linestxt, keep=True)
        self.assertEqual(data, [
            b'first line\n',
            b'second line\n',
            b'third line\n',
            b'end\n',
            ])
            
    def test_readuntil(self):
        data = uio.readuntil(self.linestxt, ' ')
        self.assertEqual(data, 'first')
        with self.assertRaises(ValueError):
            uio.readuntil(self.linestxt, '')
        data = uio.readuntil(self.linestxt, 'third')
        self.assertEqual(data, 'first line\nsecond line\n')

    def test_readbinuntil(self):
        data = uio.readbinuntil(self.linestxt, ' ')
        self.assertEqual(data, b'first')
        with self.assertRaises(ValueError):
            uio.readbinuntil(self.linestxt, '')
        data = uio.readbinuntil(self.linestxt, 'third')
        self.assertEqual(data, b'first line\nsecond line\n')

    def test_readuntil_last(self):
        data = uio.readuntil(self.linestxt, 'noop', last=True)
        self.assertEqual(data, 'first line\nsecond line\nthird line\nend\n')

    def test_readbinuntil_last(self):
        data = uio.readbinuntil(self.linestxt, 'noop', last=True)
        self.assertEqual(data, b'first line\nsecond line\nthird line\nend\n')

    def test_readuntil_keep(self):
        data = uio.readuntil(self.linestxt, ' ', keep=True)
        self.assertEqual(data, 'first ')

    def test_readbinuntil_keep(self):
        data = uio.readbinuntil(self.linestxt, ' ', keep=True)
        self.assertEqual(data, b'first ')

    def test_write(self):
        uio.write(self.path, 'abcd\0')
        self.assertEqual(self.read(), 'abcd\0')

    def test_writenum(self):
        uio.write(self.path, 1)
        self.assertEqual(self.read(), '1')

    def test_writebin(self):
        uio.writebin(self.path, b'abcd\x7f\xff')
        self.assertEqual(self.readbin(), b'abcd\x7f\xff')

    def test_writeline(self):
        uio.writeline(self.path, 'abcd\0')
        self.assertEqual(self.read(), 'abcd\0\n')

    def test_writebinline(self):
        uio.writebinline(self.path, b'abcd\x7f\xff')
        self.assertEqual(self.readbin(), b'abcd\x7f\xff\n')

    def test_writelines(self):
        uio.writelines(self.path, [b'abcd\0', 'zzz', 1])
        self.assertEqual(self.read(), 'abcd\0\nzzz\n1\n')

    def test_writebinlines(self):
        uio.writebinlines(self.path, [b'abcd\x7f\xff', 'zzz', 1])
        self.assertEqual(self.readbin(), b'abcd\x7f\xff\nzzz\n1\n')

    def test_append(self):
        uio.append(self.path, 'start')
        uio.append(self.path, 'abcd\0')
        self.assertEqual(self.read(), 'startabcd\0')

    def test_appendnum(self):
        uio.append(self.path, 'start')
        uio.append(self.path, 1)
        self.assertEqual(self.read(), 'start1')

    def test_appendbin(self):
        uio.append(self.path, 'start')
        uio.appendbin(self.path, b'abcd\x7f\xff')
        self.assertEqual(self.readbin(), b'startabcd\x7f\xff')

    def test_appendline(self):
        uio.append(self.path, 'start')
        uio.appendline(self.path, 'abcd\0')
        self.assertEqual(self.read(), 'startabcd\0\n')

    def test_appendbinline(self):
        uio.append(self.path, 'start')
        uio.appendbinline(self.path, b'abcd\x7f\xff')
        self.assertEqual(self.readbin(), b'startabcd\x7f\xff\n')

    def test_appendlines(self):
        uio.append(self.path, 'start')
        uio.appendlines(self.path, [b'abcd\0', 'zzz', 1])
        self.assertEqual(self.read(), 'startabcd\0\nzzz\n1\n')

    def test_appendbinlines(self):
        uio.append(self.path, 'start')
        uio.appendbinlines(self.path, [b'abcd\x7f\xff', 'zzz', 1])
        self.assertEqual(self.readbin(), b'startabcd\x7f\xff\nzzz\n1\n')


if __name__ == '__main__':
    unittest.main()
