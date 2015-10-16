
import unittest
import sys
import os

from imapfw.concurrency.concurrency import Concurrency
from imapfw.rascal import Rascal
from imapfw.actions.syncaccounts import SyncAccounts
from imapfw.ui.tty import TTY


def run_action(concurrency, rascal, options):
    ui = TTY(concurrency.createLock())
    ui.configure()
    ui.enableDebugCategories(options.get('debug'))
    ui.setCurrentWorkerNameFunction(lambda *args: None)
    ui.setInfoLevel(0)
    action = SyncAccounts()
    action.init(ui, concurrency, rascal, options)
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
