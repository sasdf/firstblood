import unittest
import tempfile
import os

from pathlib import Path
from firstblood import uio


dataFolder = Path(__file__).parent / 'data'


class TestLines_twt(unittest.TestCase):

    def read(self):
        with open(self.path) as f:
            return f.read()

    def setUp(self):
        fd, self.path = tempfile.mkstemp(prefix='uiotest-')
        os.close(fd)
        self.f = uio.open(self.path, 'r+')

    def tearDown(self):
        self.f.close()
        os.unlink(self.path)

    def test_rw(self):
        self.f.write('abc').write(b'def').write(1).write([1, 2])
        self.assertEqual(self.read(), 'abcdef1[1, 2]')
        data = self.f.seek(0).read()
        self.assertEqual(data, 'abcdef1[1, 2]')
        with self.assertRaises(EOFError):
            self.f.read()


if __name__ == '__main__':
    unittest.main()
