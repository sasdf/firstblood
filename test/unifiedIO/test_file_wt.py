import unittest
import tempfile
import os

from pathlib import Path
from firstblood import uio


dataFolder = Path(__file__).parent / 'data'


class TestLines_wt(unittest.TestCase):

    def read(self):
        with open(self.path) as f:
            return f.read()

    def setUp(self):
        fd, self.path = tempfile.mkstemp(prefix='uiotest-')
        os.close(fd)
        self.f = uio.open(self.path, 'w')

    def tearDown(self):
        self.f.close()
        os.unlink(self.path)

    def test_write(self):
        self.f.write('abc').write(b'def').write(1).write([1, 2])
        self.assertEqual(self.read(), 'abcdef1[1, 2]')
        self.f.write('zzz').write('').close()
        self.assertEqual(self.read(), 'abcdef1[1, 2]zzz')
        with self.assertRaises(ValueError):
            self.f.write('noop')

    def test_write_nonascii(self):
        self.f.write('abc\x00').write(b'\x01')
        self.assertEqual(self.read(), 'abc\0\x01')
        self.f.write('zzz').close()
        self.assertEqual(self.read(), 'abc\0\x01zzz')
        with self.assertRaises(ValueError):
            self.f.write('noop')

    def test_writeline(self):
        self.f.write('abc').line('def')
        self.assertEqual(self.read(), 'abcdef\n')
        self.f.line('zzz').line('').close()
        self.assertEqual(self.read(), 'abcdef\nzzz\n\n')
        with self.assertRaises(ValueError):
            self.f.line('noop')

    def test_writelines(self):
        self.f.write('abc').lines(['def', b'ghi', 1, [1, 2]])
        self.assertEqual(self.read(), 'abcdef\nghi\n1\n[1, 2]\n')
        self.f.line('zzz').close()
        self.assertEqual(self.read(), 'abcdef\nghi\n1\n[1, 2]\nzzz\n')
        with self.assertRaises(ValueError):
            self.f.line('noop')

    def test_endl(self):
        self.f.write('abc').endl().lines(['def', b'ghi', 1, [1, 2]])
        self.assertEqual(self.read(), 'abc\ndef\nghi\n1\n[1, 2]\n')
        self.f.line('zzz').endl().endl().close()
        self.assertEqual(self.read(), 'abc\ndef\nghi\n1\n[1, 2]\nzzz\n\n\n')
        with self.assertRaises(ValueError):
            self.f.line('noop')

    def test_pipe(self):
        with uio.open(dataFolder / 'lines.txt') as lines:
            cleanup, stop = lines.pipe(self.f)
            stop.wait()
            cleanup()
            self.assertEqual(self.read(), 'first line\nsecond line\nthird line\nend\n')

    def test_pipe_block(self):
        with uio.open(dataFolder / 'lines.txt') as lines:
            lines = uio.open(dataFolder / 'lines.txt')
            lines.pipe(self.f, block=True)
            self.assertEqual(self.read(), 'first line\nsecond line\nthird line\nend\n')


if __name__ == '__main__':
    unittest.main()
