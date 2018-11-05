import unittest
import time

from firstblood import uio


class TestLines_wt(unittest.TestCase):

    def assertRange(self, val, expected, err):
        self.assertLess(val, expected + err)
        self.assertGreater(val, expected - err)

    def tearDown(self):
        if hasattr(self, 'r'):
            self.r.kill()
            self.r.close()

    def test_shell(self):
        self.r = r = uio.spawn('printf "abc\\0"; printf "def";')
        data = r.read()
        self.assertEqual(data, 'abc\0def')
        
    def test_read(self):
        self.r = r = uio.spawn(['printf', 'abc\\0'])
        data = r.read()
        self.assertEqual(data, 'abc\0')

    def test_readbin(self):
        self.r = r = uio.spawn(['printf', 'abc\\x7f\\xff'], encoding=None)
        data = r.read()
        self.assertEqual(data, b'abc\x7f\xff')

    def test_readline(self):
        self.r = r = uio.spawn(['printf', 'abc\\n\\0'])
        data = r.line()
        self.assertEqual(data, 'abc')
        data = r.line()
        self.assertEqual(data, '\0')

    def test_until(self):
        self.r = r = uio.spawn(['printf', 'abc\\n\\0next: def'])
        data = r.until('next: ')
        self.assertEqual(data, 'abc\n\0')
        data = r.line()
        self.assertEqual(data, 'def')

    def test_write(self):
        self.r = r = uio.spawn('cat')
        data = r.write('abc').close('write').read()
        self.assertEqual(data, 'abc')

    def test_writebin(self):
        self.r = r = uio.spawn('cat', encoding=None)
        data = r.write(b'abc\x7f\xff').close('write').read()
        self.assertEqual(data, b'abc\x7f\xff')

    def test_writeline(self):
        self.r = r = uio.spawn('cat')
        data = r.line('abc').line('\0').close('write').line()
        self.assertEqual(data, 'abc')
        data = r.line()
        self.assertEqual(data, '\0')

    def test_before(self):
        self.r = r = uio.spawn('printf "out: 0x1234\\n"; cat')
        data = r.before('0x').line(0).line()
        self.assertEqual(data, '0x1234')
        data = r.line()
        self.assertEqual(data, '0')
        
    def test_after(self):
        self.r = r = uio.spawn('printf "out: abcd\\n"; cat')
        data = r.after('out: ').line(0).line()
        self.assertEqual(data, 'abcd')
        data = r.line()
        self.assertEqual(data, '0')

    def test_wait(self):
        start = time.time()
        self.r = r = uio.spawn('sleep .1')
        r.wait()
        duration = time.time() - start
        self.assertRange(duration, 0.1, 0.02)

    def test_some(self):
        start = time.time()
        self.r = r = uio.spawn('printf "abc"; sleep .1; printf "def"')
        data = r.some()
        self.assertEqual(data, 'abc')
        data = r.some()
        self.assertEqual(data, 'def')

    def test_timeout(self):
        start = time.time()
        self.r = r = uio.spawn('sleep .1')
        with r.timeout(0.05):
            r.wait()
        duration = time.time() - start
        self.assertRange(duration, 0.05, 0.01)

    def test_timeout_total(self):
        start = time.time()
        self.r = r = uio.spawn('printf "abc"; sleep .1;'*2)
        with r.timeout(total=0.12) as timer:
            data = r.some()
            self.assertEqual(data, 'abc')
            data = r.some()
            self.assertEqual(data, 'abc')
        self.assertTrue(timer.safe)

    def test_timeout_total_fail(self):
        start = time.time()
        self.r = r = uio.spawn('printf "abc"; sleep .1;'*3)
        with r.timeout(total=0.12) as timer:
            data = r.some()
            self.assertEqual(data, 'abc')
            data = r.some()
            self.assertEqual(data, 'abc')
            r.some()
            self.fail('Not timeout')
        self.assertFalse(timer.safe)

    def test_kill(self):
        start = time.time()
        self.r = r = uio.spawn('sleep 10')
        r.kill()
        r.wait()
        duration = time.time() - start
        self.assertLess(duration, 0.1)
        self.assertEqual(r.returncode, -9)

    def test_terminate(self):
        start = time.time()
        self.r = r = uio.spawn('sleep 10')
        r.terminate()
        r.wait()
        duration = time.time() - start
        self.assertLess(duration, 0.1)
        self.assertEqual(r.returncode, -15)

    def test_signal(self):
        start = time.time()
        self.r = r = uio.spawn('sleep 10')
        r.signal(14)  # SIGALRM
        r.wait()
        duration = time.time() - start
        self.assertLess(duration, 0.1)
        self.assertEqual(r.returncode, -14)

    def test_pid(self):
        self.r = r = uio.spawn('sleep 10')
        self.assertIsInstance(r.pid, int)

    def test_close_out(self):
        self.r = r = uio.spawn('printf "abc"; read val; sleep $val')
        data = r.some()
        self.assertEqual(data, 'abc')
        r.close(dir='in')
        with self.assertRaises(ValueError):
            r.read(1)
        start = time.time()
        r.line('.1')
        with r.timeout(1):
            r.wait()
        duration = time.time() - start
        self.assertRange(duration, 0.1, 0.02)

    def test_close_KeyError(self):
        self.r = r = uio.spawn('printf "abc"; read val; sleep $val')
        with self.assertRaises(KeyError):
            r.close(dir='noop')

    def test_context(self):
        with uio.spawn('printf "abc"; read val;') as r:
            data = r.some()
            self.assertEqual(data, 'abc')
        with self.assertRaises(ValueError):
            r.read(1)


if __name__ == '__main__':
    unittest.main()
