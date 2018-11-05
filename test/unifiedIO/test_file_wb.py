import unittest
import tempfile
import os

from firstblood import uio


class TestLines_wt(unittest.TestCase):

    def read(self):
        with open(self.path, 'rb') as f:
            return f.read()

    def setUp(self):
        fd, self.path = tempfile.mkstemp(prefix='uiotest-')
        os.close(fd)
        self.f = uio.open(self.path, 'wb')

    def tearDown(self):
        self.f.close()
        os.unlink(self.path)

    def test_write(self):
        self.f.write('abc').write(b'def').write(1).write([1, 2])
        self.assertEqual(self.read(), b'abcdef1[1, 2]')
        self.f.write('zzz').write('').close()
        self.assertEqual(self.read(), b'abcdef1[1, 2]zzz')
        with self.assertRaises(ValueError):
            self.f.write('noop')

    def test_write_nonascii(self):
        self.f.write('abc\x00').write(b'\x01').write(b'\x7f\xff')
        self.assertEqual(self.read(), b'abc\0\x01\x7f\xff')
        self.f.write('zzz').close()
        self.assertEqual(self.read(), b'abc\0\x01\x7f\xffzzz')
        with self.assertRaises(ValueError):
            self.f.write('noop')

    def test_writeline(self):
        self.f.write('abc').line('def')
        self.assertEqual(self.read(), b'abcdef\n')
        self.f.line('zzz').line('').close()
        self.assertEqual(self.read(), b'abcdef\nzzz\n\n')
        with self.assertRaises(ValueError):
            self.f.line('noop')

    def test_writelines(self):
        self.f.write('abc').lines(['def', b'ghi', 1, [1, 2]])
        self.assertEqual(self.read(), b'abcdef\nghi\n1\n[1, 2]\n')
        self.f.line('zzz').close()
        self.assertEqual(self.read(), b'abcdef\nghi\n1\n[1, 2]\nzzz\n')
        with self.assertRaises(ValueError):
            self.f.line('noop')

    def test_endl(self):
        self.f.write('abc').endl().lines(['def', b'ghi', 1, [1, 2]])
        self.assertEqual(self.read(), b'abc\ndef\nghi\n1\n[1, 2]\n')
        self.f.line('zzz').endl().endl().close()
        self.assertEqual(self.read(), b'abc\ndef\nghi\n1\n[1, 2]\nzzz\n\n\n')
        with self.assertRaises(ValueError):
            self.f.line('noop')


if __name__ == '__main__':
    unittest.main()
