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
import time

from imapfw import runtime
from imapfw.edmp import *


class TestEDMP(unittest.TestCase):
    def setUp(self):
        self.c = runtime.concurrency

    def test_channel(self):
        queue = self.c.createQueue()
        for i in range(3):
            queue.put(i)
        chan = Channel(queue)

        # The internal channel queue.get_nowait() might be racy with
        # multiprocessing. Sleeping for 0.1 secs should be enough but this is
        # still RACY.
        time.sleep(0.1)
        self.assertEqual([x for x in chan], [0, 1, 2])

    def test_newEmitterReceiver(self):
        r, e = newEmitterReceiver('test')
        self.assertIsInstance(r, Receiver)
        self.assertIsInstance(e, Emitter)

    def test_event(self):
        def onEvent(true):
            self.assertEqual(true, True)

        r, e = newEmitterReceiver('test')
        r.accept('event', onEvent)
        e.event(True)
        e.stopServing()
        while r.react():
            pass

    def test_event_multiple_args(self):
        def onEvent(true, false, none=False):
            self.assertEqual(true, True)
            self.assertEqual(false, False)
            self.assertEqual(none, None)

        r, e = newEmitterReceiver('test')
        r.accept('event', onEvent)
        e.event(True, False, none=None)
        e.stopServing()
        while r.react():
            pass

    def test_event_receiver_arg(self):
        def onEvent(true):
            self.assertEqual(true, True)

        r, e = newEmitterReceiver('test')
        r.accept('event', onEvent, True)
        e.event()
        e.stopServing()
        while r.react():
            pass

    def test_event_receiver_args(self):
        def onEvent(true, false):
            self.assertEqual(true, True)
            self.assertEqual(false, False)

        r, e = newEmitterReceiver('test')
        r.accept('event', onEvent, True, False)
        e.event()
        e.stopServing()
        while r.react():
            pass

    def test_event_emitter_receiver_args(self):
        def onEvent(eight, nine, one, two, three):
            self.assertEqual(one, 1)
            self.assertEqual(two, 2)
            self.assertEqual(three, 3)
            self.assertEqual(eight, 8)
            self.assertEqual(nine, 9)

        r, e = newEmitterReceiver('test')
        r.accept('event', onEvent, 8, 9)
        e.event(1, 2, 3)
        e.stopServing()
        while r.react():
            pass

    def test_event_errors(self):
        def onEvent():
            raise RuntimeError('error')

        r, e = newEmitterReceiver('test')
        r.accept('event', onEvent, True, False)
        e.event()
        e.stopServing()

        # Must not raise anything.
        while r.react():
            pass

    def test_event_errors_sync(self):
        def onEvent():
            raise RuntimeError('error')

        def runner(r):
            while r.react():
                pass

        r, e = newEmitterReceiver('test')
        r.accept('event', onEvent)
        w = self.c.createWorker('runner', runner, (r,))
        w.start()

        # Must raise error.
        self.assertRaises(RuntimeError, e.event_sync)
        e.stopServing()
        w.join()


if __name__ == '__main__':
    unittest.main(verbosity=2)
