import unittest
from pathlib import Path

from firstblood import uio


dataFolder = Path(__file__).parent / 'data'


class TestLines_rb(unittest.TestCase):

    def setUp(self):
        self.f = uio.open(dataFolder / 'lines.txt', 'rb')

    def tearDown(self):
        self.f.close()

    def test_read(self):
        data = self.f.read()
        self.assertEqual(data, b'first line\nsecond line\nthird line\nend\n')
        with self.assertRaises(EOFError):
            data = self.f.read(1)

    def test_readn(self):
        data = self.f.read(20)
        self.assertEqual(data, b'first line\nsecond li')
        data = self.f.read(10)
        self.assertEqual(data, b'ne\nthird l')
        data = self.f.read(0)
        self.assertEqual(data, b'')
        with self.assertRaises(EOFError):
            self.f.read(10)
        data = self.f.read(0)
        self.assertEqual(data, b'')

    def test_peek_nobuf(self):
        data = self.f.peek(0)
        self.assertEqual(data, b'')
        data = self.f.peek(20)
        self.assertEqual(data, b'first line\nsecond li')
        data = self.f.peek(10)
        self.assertEqual(data, b'first line')
        data = self.f.read(20)
        self.assertEqual(data, b'first line\nsecond li')
        data = self.f.read(10)
        self.assertEqual(data, b'ne\nthird l')

    def test_peek(self):
        data = self.f.read(20)
        self.assertEqual(data, b'first line\nsecond li')
        data = self.f.peek(10)
        self.assertEqual(data, b'ne\nthird l')
        data = self.f.read(10)
        self.assertEqual(data, b'ne\nthird l')
        self.f.read()
        with self.assertRaises(EOFError):
            self.f.peek(10)

    def test_line(self):
        data = self.f.line()
        self.assertEqual(data, b'first line')
        data = self.f.line()
        self.assertEqual(data, b'second line')
        self.f.read()
        with self.assertRaises(EOFError):
            self.f.line()

    def test_line_keep(self):
        data = self.f.line(keep=True)
        self.assertEqual(data, b'first line\n')
        data = self.f.line(keep=True)
        self.assertEqual(data, b'second line\n')
        self.f.read()
        with self.assertRaises(EOFError):
            self.f.line(keep=True)

    def test_lines_nobuf(self):
        data = self.f.lines()
        self.assertEqual(data, [
            b'first line',
            b'second line',
            b'third line',
            b'end',
            ])
        with self.assertRaises(EOFError):
            self.f.lines()

    def test_lines(self):
        data = self.f.line()
        self.assertEqual(data, b'first line')
        data = self.f.lines()
        self.assertEqual(data, [
            b'second line',
            b'third line',
            b'end',
            ])
        with self.assertRaises(EOFError):
            self.f.lines()

    def test_lines_keep_nobuf(self):
        data = self.f.lines(keep=True)
        self.assertEqual(data, [
            b'first line\n',
            b'second line\n',
            b'third line\n',
            b'end\n',
            ])
        with self.assertRaises(EOFError):
            self.f.lines(keep=True)

    def test_lines_keep(self):
        data = self.f.line()
        self.assertEqual(data, b'first line')
        data = self.f.lines(keep=True)
        self.assertEqual(data, [
            b'second line\n',
            b'third line\n',
            b'end\n',
            ])
        with self.assertRaises(EOFError):
            self.f.lines(keep=True)

    def test_readuntil(self):
        data = self.f.readuntil(b' ')
        self.assertEqual(data, b'first')
        with self.assertRaises(ValueError):
            self.f.readuntil(b'')
        data = self.f.line()
        self.assertEqual(data, b'line')
        data = self.f.readuntil(b'line')
        self.assertEqual(data, b'second ')
        with self.assertRaises(EOFError):
            self.f.readuntil(b'noop')

    def test_readuntil_str(self):
        data = self.f.readuntil(' ')
        self.assertEqual(data, b'first')
        with self.assertRaises(ValueError):
            self.f.readuntil('')
        data = self.f.line()
        self.assertEqual(data, b'line')
        data = self.f.readuntil('line')
        self.assertEqual(data, b'second ')
        with self.assertRaises(EOFError):
            self.f.readuntil('noop')

    def test_readuntil_last(self):
        data = self.f.readuntil(b' ')
        self.assertEqual(data, b'first')
        data = self.f.readuntil(b'noop', last=True)
        self.assertEqual(data, b'line\nsecond line\nthird line\nend\n')
        with self.assertRaises(EOFError):
            self.f.readuntil(b'noop', last=True)

    def test_readuntil_keep(self):
        data = self.f.readuntil(b' ', keep=True)
        self.assertEqual(data, b'first ')
        data = self.f.line()
        self.assertEqual(data, b'line')
        data = self.f.readuntil(b'line', keep=True)
        self.assertEqual(data, b'second line')
        with self.assertRaises(EOFError):
            self.f.readuntil(b'noop', keep=True)

    def test_readuntil_nondrop(self):
        data = self.f.readuntil(b' ', drop=False)
        self.assertEqual(data, b'first')
        data = self.f.line()
        self.assertEqual(data, b' line')
        data = self.f.readuntil(b'line', drop=False)
        self.assertEqual(data, b'second ')
        data = self.f.line()
        self.assertEqual(data, b'line')
        with self.assertRaises(EOFError):
            self.f.readuntil(b'noop', drop=False)

    def test_readuntil_keepoverwrite(self):
        data = self.f.readuntil(b' ', keep=True, drop=False)
        self.assertEqual(data, b'first ')
        data = self.f.line()
        self.assertEqual(data, b'line')
        data = self.f.readuntil(b'line', keep=True, drop=False)
        self.assertEqual(data, b'second line')
        data = self.f.line()
        self.assertEqual(data, b'')
        with self.assertRaises(EOFError):
            self.f.readuntil(b'noop', keep=True, drop=False)

    def test_until(self):
        data = self.f.until(b' ')
        self.assertEqual(data, b'first')
        data = self.f.line()
        self.assertEqual(data, b'line')
        data = self.f.until(b'line')
        self.assertEqual(data, b'second ')
        with self.assertRaises(EOFError):
            self.f.until(b'noop')

    def test_before(self):
        data = self.f.before(b' ').line()
        self.assertEqual(data, b' line')
        data = self.f.before(b'line').line()
        self.assertEqual(data, b'line')
        with self.assertRaises(EOFError):
            self.f.before(b'noop')

    def test_after(self):
        data = self.f.after(b' ').line()
        self.assertEqual(data, b'line')
        data = self.f.after(b'line').line()
        self.assertEqual(data, b'')
        with self.assertRaises(EOFError):
            self.f.after(b'noop')

    def test_nextline(self):
        data = self.f.nextline().line()
        self.assertEqual(data, b'second line')
        data = self.f.nextline().line()
        self.assertEqual(data, b'end')
        with self.assertRaises(EOFError):
            self.f.nextline()
            
    def test_close(self):
        this = self.f.close()
        self.assertEqual(this, self.f)
        with self.assertRaises(ValueError):
            self.f.read()

    def test_context(self):
        with self.f:
            data = self.f.read(10)
            self.assertEqual(data, b'first line')
        with self.assertRaises(ValueError):
            self.f.read()

    def test_timeout(self):
        with self.f.timeout(0) as timer:
            data = self.f.line()
            self.assertEqual(data, b'first line')
        self.assertTrue(timer.safe)
        with self.f.timeout(total=1) as timer:
            data = self.f.line()
            self.assertEqual(data, b'second line')
        self.assertTrue(timer.safe)

    def test_seek(self):
        data = self.f.nextline().line()
        self.assertEqual(data, b'second line')
        data = self.f.seek(0).line()
        self.assertEqual(data, b'first line')
        data = self.f.seek(2).line()
        self.assertEqual(data, b'rst line')
        with self.assertRaises(EOFError):
            self.f.seek(10000).line()


if __name__ == '__main__':
    unittest.main()
