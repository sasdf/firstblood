import unittest
from pathlib import Path

from firstblood import uio


dataFolder = Path(__file__).parent / 'data'


class TestLines_rt(unittest.TestCase):

    def setUp(self):
        self.f = uio.open(dataFolder / 'lines.txt')

    def tearDown(self):
        self.f.close()

    def test_read(self):
        data = self.f.read()
        self.assertEqual(data, 'first line\nsecond line\nthird line\nend\n')
        with self.assertRaises(EOFError):
            data = self.f.read(1)

    def test_readn(self):
        data = self.f.read(20)
        self.assertEqual(data, 'first line\nsecond li')
        data = self.f.read(10)
        self.assertEqual(data, 'ne\nthird l')
        data = self.f.read(0)
        self.assertEqual(data, '')
        with self.assertRaises(EOFError):
            self.f.read(10)
        data = self.f.read(0)
        self.assertEqual(data, '')

    def test_peek_nobuf(self):
        data = self.f.peek(0)
        self.assertEqual(data, '')
        data = self.f.peek(20)
        self.assertEqual(data, 'first line\nsecond li')
        data = self.f.peek(10)
        self.assertEqual(data, 'first line')
        data = self.f.read(20)
        self.assertEqual(data, 'first line\nsecond li')
        data = self.f.read(10)
        self.assertEqual(data, 'ne\nthird l')

    def test_peek(self):
        data = self.f.read(20)
        self.assertEqual(data, 'first line\nsecond li')
        data = self.f.peek(10)
        self.assertEqual(data, 'ne\nthird l')
        data = self.f.read(10)
        self.assertEqual(data, 'ne\nthird l')
        self.f.read()
        with self.assertRaises(EOFError):
            self.f.peek(10)

    def test_line(self):
        data = self.f.line()
        self.assertEqual(data, 'first line')
        data = self.f.line()
        self.assertEqual(data, 'second line')
        self.f.read()
        with self.assertRaises(EOFError):
            self.f.line()

    def test_line_keep(self):
        data = self.f.line(keep=True)
        self.assertEqual(data, 'first line\n')
        data = self.f.line(keep=True)
        self.assertEqual(data, 'second line\n')
        self.f.read()
        with self.assertRaises(EOFError):
            self.f.line(keep=True)

    def test_lines_nobuf(self):
        data = self.f.lines()
        self.assertEqual(data, [
            'first line',
            'second line',
            'third line',
            'end',
            ])
        with self.assertRaises(EOFError):
            self.f.lines()

    def test_lines(self):
        data = self.f.line()
        self.assertEqual(data, 'first line')
        data = self.f.lines()
        self.assertEqual(data, [
            'second line',
            'third line',
            'end',
            ])
        with self.assertRaises(EOFError):
            self.f.lines()

    def test_lines_keep_nobuf(self):
        data = self.f.lines(keep=True)
        self.assertEqual(data, [
            'first line\n',
            'second line\n',
            'third line\n',
            'end\n',
            ])
        with self.assertRaises(EOFError):
            self.f.lines(keep=True)

    def test_lines_keep(self):
        data = self.f.line()
        self.assertEqual(data, 'first line')
        data = self.f.lines(keep=True)
        self.assertEqual(data, [
            'second line\n',
            'third line\n',
            'end\n',
            ])
        with self.assertRaises(EOFError):
            self.f.lines(keep=True)

    def test_readuntil(self):
        data = self.f.readuntil(' ')
        self.assertEqual(data, 'first')
        with self.assertRaises(ValueError):
            self.f.readuntil('')
        data = self.f.line()
        self.assertEqual(data, 'line')
        data = self.f.readuntil('line')
        self.assertEqual(data, 'second ')
        with self.assertRaises(EOFError):
            self.f.readuntil('noop')

    def test_readuntil_bytes(self):
        data = self.f.readuntil(b' ')
        self.assertEqual(data, 'first')
        with self.assertRaises(ValueError):
            self.f.readuntil(b'')
        data = self.f.line()
        self.assertEqual(data, 'line')
        data = self.f.readuntil(b'line')
        self.assertEqual(data, 'second ')
        with self.assertRaises(EOFError):
            self.f.readuntil(b'noop')

    def test_readuntil_last(self):
        data = self.f.readuntil(' ')
        self.assertEqual(data, 'first')
        data = self.f.readuntil('noop', last=True)
        self.assertEqual(data, 'line\nsecond line\nthird line\nend\n')
        with self.assertRaises(EOFError):
            self.f.readuntil('noop', last=True)

    def test_readuntil_keep(self):
        data = self.f.readuntil(' ', keep=True)
        self.assertEqual(data, 'first ')
        data = self.f.line()
        self.assertEqual(data, 'line')
        data = self.f.readuntil('line', keep=True)
        self.assertEqual(data, 'second line')
        with self.assertRaises(EOFError):
            self.f.readuntil('noop', keep=True)

    def test_readuntil_nondrop(self):
        data = self.f.readuntil(' ', drop=False)
        self.assertEqual(data, 'first')
        data = self.f.line()
        self.assertEqual(data, ' line')
        data = self.f.readuntil('line', drop=False)
        self.assertEqual(data, 'second ')
        data = self.f.line()
        self.assertEqual(data, 'line')
        with self.assertRaises(EOFError):
            self.f.readuntil('noop', drop=False)

    def test_readuntil_keepoverwrite(self):
        data = self.f.readuntil(' ', keep=True, drop=False)
        self.assertEqual(data, 'first ')
        data = self.f.line()
        self.assertEqual(data, 'line')
        data = self.f.readuntil('line', keep=True, drop=False)
        self.assertEqual(data, 'second line')
        data = self.f.line()
        self.assertEqual(data, '')
        with self.assertRaises(EOFError):
            self.f.readuntil('noop', keep=True, drop=False)

    def test_until(self):
        data = self.f.until(' ')
        self.assertEqual(data, 'first')
        data = self.f.line()
        self.assertEqual(data, 'line')
        data = self.f.until('line')
        self.assertEqual(data, 'second ')
        with self.assertRaises(EOFError):
            self.f.until('noop')

    def test_before(self):
        data = self.f.before(' ').line()
        self.assertEqual(data, ' line')
        data = self.f.before('line').line()
        self.assertEqual(data, 'line')
        with self.assertRaises(EOFError):
            self.f.before('noop')

    def test_after(self):
        data = self.f.after(' ').line()
        self.assertEqual(data, 'line')
        data = self.f.after('line').line()
        self.assertEqual(data, '')
        with self.assertRaises(EOFError):
            self.f.after('noop')

    def test_nextline(self):
        data = self.f.nextline().line()
        self.assertEqual(data, 'second line')
        data = self.f.nextline().line()
        self.assertEqual(data, 'end')
        with self.assertRaises(EOFError):
            self.f.nextline()

    def test_seek(self):
        data = self.f.nextline().line()
        self.assertEqual(data, 'second line')
        data = self.f.seek(0).line()
        self.assertEqual(data, 'first line')
        data = self.f.seek(2).line()
        self.assertEqual(data, 'rst line')
        with self.assertRaises(EOFError):
            self.f.seek(10000).line()


class TestBrokenLine_rt(unittest.TestCase):

    def setUp(self):
        self.f = uio.open(dataFolder / 'broken-lines.txt')

    def tearDown(self):
        self.f.close()

    def test_read(self):
        data = self.f.read()
        self.assertEqual(data, 'first line\nbroken line')
        with self.assertRaises(EOFError):
            self.f.read()

    def test_line(self):
        data = self.f.line()
        self.assertEqual(data, 'first line')
        data = self.f.line()
        self.assertEqual(data, 'broken line')
        with self.assertRaises(EOFError):
            self.f.line()

    def test_line_keep(self):
        data = self.f.line(keep=True)
        self.assertEqual(data, 'first line\n')
        data = self.f.line(keep=True)
        self.assertEqual(data, 'broken line')
        with self.assertRaises(EOFError):
            self.f.line()

    def test_lines(self):
        data = self.f.lines()
        self.assertEqual(data, ['first line', 'broken line'])
        with self.assertRaises(EOFError):
            self.f.line()

    def test_lines_keep(self):
        data = self.f.lines(keep=True)
        self.assertEqual(data, ['first line\n', 'broken line'])
        with self.assertRaises(EOFError):
            self.f.line()


class TestUni_rt(unittest.TestCase):

    def setUp(self):
        self.f = uio.open(dataFolder / 'uni.txt')

    def tearDown(self):
        self.f.close()

    def test_read(self):
        data = self.f.read()
        self.assertEqual(data, '\U0001f600\U0001f601\U0001f602')
        with self.assertRaises(EOFError):
            self.f.read()

    def test_readn(self):
        data = self.f.read(1)
        self.assertEqual(data, '\U0001f600')
        data = self.f.read(2)
        self.assertEqual(data, '\U0001f601\U0001f602')
        with self.assertRaises(EOFError):
            self.f.read(1)

    def test_line(self):
        data = self.f.line()
        self.assertEqual(data, '\U0001f600\U0001f601\U0001f602')
        with self.assertRaises(EOFError):
            self.f.line()

    def test_lines(self):
        data = self.f.lines()
        self.assertEqual(data, ['\U0001f600\U0001f601\U0001f602'])
        with self.assertRaises(EOFError):
            self.f.line()

    def test_until(self):
        data = self.f.until('\U0001f601')
        self.assertEqual(data, '\U0001f600')
        with self.assertRaises(EOFError):
            self.f.until('noop')

    def test_seek(self):
        data = self.f.read(1)
        self.assertEqual(data, '\U0001f600')
        data = self.f.read(2)
        self.assertEqual(data, '\U0001f601\U0001f602')
        data = self.f.seek(4).read(2)
        self.assertEqual(data, '\U0001f601\U0001f602')
        with self.assertRaises(UnicodeDecodeError):
            self.f.seek(2).read()


class TestBrokenUni_rt(unittest.TestCase):

    def setUp(self):
        self.f = uio.open(dataFolder / 'broken-uni.txt')

    def tearDown(self):
        self.f.close()

    def test_read(self):
        with self.assertRaises(UnicodeDecodeError):
            self.f.read()

    def test_readn(self):
        data = self.f.read(2)
        self.assertEqual(data, '\U0001f600\U0001f601')
        with self.assertRaises(UnicodeDecodeError):
            self.f.read(1)

    def test_line(self):
        with self.assertRaises(UnicodeDecodeError):
            self.f.line()

    def test_lines(self):
        with self.assertRaises(UnicodeDecodeError):
            self.f.line()

    def test_until(self):
        with self.assertRaises(UnicodeDecodeError):
            self.f.until('noop')


if __name__ == '__main__':
    unittest.main()
