# The MIT License (MIT)
#
# Copyright (c) 2015, Nicolas Sebrecht & contributors
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import unittest

from imapfw import runtime
from imapfw.concurrency.concurrency import *


class TestConcurrency(unittest.TestCase):
    def setUp(self):
        def noop():
            pass

        def blocking():
            while True:
                pass

        self.noop = noop
        self.blocking = blocking

    def test_00_concurrency_interface(self):
        self.assertIsInstance(runtime.concurrency, ConcurrencyInterface)

    def test_01_queue_interface(self):
        self.assertIsInstance(runtime.concurrency.createQueue(), QueueInterface)

    def test_02_lock_interface(self):
        self.assertIsInstance(runtime.concurrency.createLock(), LockBase)

    def test_03_worker_interface(self):
        self.assertIsInstance(
            runtime.concurrency.createWorker('noop', self.noop, ()),
            WorkerInterface)

    def test_04_worker_start_join(self):
        worker = runtime.concurrency.createWorker('noop', self.noop, ())

        worker.start()
        self.assertEqual(worker.getName(), 'noop')

        worker.join()

    def test_05_worker_start_kill(self):
        worker = runtime.concurrency.createWorker('blocking', self.blocking, ())

        worker.start()
        self.assertEqual(worker.getName(), 'blocking')

        worker.kill()


if __name__ == '__main__':
    unittest.main(verbosity=2)
