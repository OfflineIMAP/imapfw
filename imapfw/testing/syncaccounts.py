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
import sys
import os

from imapfw import runtime

from imapfw.concurrency.concurrency import Concurrency
from imapfw.rascal import Rascal
from imapfw.actions.syncaccounts import SyncAccounts
from imapfw.ui.tty import TTY


def run_action(rascal, concurrency, options):
    ui = TTY(runtime.concurrency.createLock())
    ui.configure()
    ui.enableDebugCategories(options.get('debug'))
    ui.setCurrentWorkerNameFunction(lambda *args: None)
    ui.setInfoLevel(3)

    runtime.set_module('ui', ui)

    action = SyncAccounts()
    action.init(options)
    action.run()
    return action.getExitCode()

#
# Check the tests manually:
# imapfw.py -r imapfw/testing/rascals/syncaccounts.1.rascal -d all syncAccounts -a AccountA
#
class TestSyncAccounts(unittest.TestCase):
    def setUp(self):
        def loadRascal(path):
            rascal = Rascal()
            rascal.load(path)
            runtime.set_module('rascal', rascal)
            return rascal

        imapfw_path = os.path.abspath(sys.modules['imapfw'].__path__[0])
        rascalsDir = os.path.join(
            imapfw_path,
            'testing',
            'rascals',
            )

        self.multiprocessing = Concurrency('multiprocessing')
        self.threading = Concurrency('threading')
        self.rascal = loadRascal(os.path.join(rascalsDir, 'syncaccounts.1.rascal'))

    def test_runAccountA_multiprocessing(self):
        self.assertEqual(0, run_action(self.multiprocessing, self.rascal,
            {'accounts': ['AccountA'], 'debug': []} ))

    def test_runAccountA_threading(self):
        self.assertEqual(0, run_action(self.threading, self.rascal,
            {'accounts': ['AccountA'], 'debug': []} ))

    def test_runAccountA_multiprocessing_debugAll(self):
        self.assertEqual(0, run_action(self.multiprocessing, self.rascal,
            {'accounts': ['AccountA'], 'debug': ['all']} ))

    def test_runAccountA_threading_debugAll(self):
        self.assertEqual(0, run_action(self.threading, self.rascal,
            {'accounts': ['AccountA'], 'debug': ['all']} ))
