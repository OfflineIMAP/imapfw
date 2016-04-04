# The MIT License (MIT).
# Copyright (c) 2015-2006, Nicolas Sebrecht & contributors.

import unittest

from imapfw import runtime
from imapfw.architects.architect import Architect
from imapfw.architects.engine import EngineArchitect
from imapfw.architects.driver import DriverArchitect, DriversArchitect
from imapfw.edmp import Emitter


class TestArchitect(unittest.TestCase):
    def setUp(self):
        self.arc = Architect('testWorker')

    def test_00_start_stop(self):
        def runner():
            pass

        self.arc.start(runner, ())
        self.arc.stop()

    def test_01_start_kill(self):
        def runner():
            while True:
                pass

        self.arc.start(runner, ())
        self.arc.kill()


class TestDriverArchitect(unittest.TestCase):
    def setUp(self):
        self.arc = DriverArchitect('Driver')

    def test_00_start_stop(self):
        self.arc.init()
        self.arc.start()
        self.arc.stop()

    def test_01_start_kill(self):
        self.arc.init()
        self.arc.start()
        self.arc.kill()

    def test_02_getEmitter(self):
        self.assertRaises(AssertionError, self.arc.getEmitter)
        self.arc.init()
        emitter = self.arc.getEmitter()
        self.assertIsInstance(emitter, Emitter)


class TestDriversArchitect(unittest.TestCase):
    def setUp(self):
        self.arc = DriversArchitect('Drivers', 3)

    def test_00_start_stop(self):
        self.arc.init()
        self.arc.start()
        self.arc.stop()

    def test_01_start_kill(self):
        self.arc.init()
        self.arc.start()
        self.arc.kill()

    def test_02_getEmitter(self):
        self.assertRaises(KeyError, self.arc.getEmitter, 0)
        self.arc.init()
        emitter = self.arc.getEmitter(0)
        self.assertIsInstance(emitter, Emitter)
        emitter = self.arc.getEmitter(1)
        self.assertIsInstance(emitter, Emitter)
        emitter = self.arc.getEmitter(2)
        self.assertIsInstance(emitter, Emitter)
        self.assertRaises(KeyError, self.arc.getEmitter, 3)

class TestEngineArchitect(unittest.TestCase):
    def setUp(self):
        def runner():
            pass

        self.runner = runner
        self.arc = EngineArchitect('Engine')

    def test_00_start_stop(self):
        self.arc.init()
        self.arc.start(self.runner, ())
        self.arc.stop()

    def test_01_start_kill(self):
        self.arc.init()
        self.arc.start(self.runner, ())
        self.arc.kill()

    def test_02_getEmitter(self):
        self.arc.init()
        emitter = self.arc.getLeftEmitter()
        self.assertIsInstance(emitter, Emitter)
        emitter = self.arc.getRightEmitter()
        self.assertIsInstance(emitter, Emitter)


if __name__ == '__main__':
    from imapfw.concurrency import Concurrency
    from imapfw.ui.tty import TTY

    runtime.set_module('concurrency', Concurrency('multiprocessing'))
    ui = TTY(runtime.concurrency.createLock())
    ui.configure()
    # ui.enableDebugCategories(['architects'])
    runtime.set_module('ui', ui)
    unittest.main(verbosity=2)
