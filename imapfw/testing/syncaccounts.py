
import unittest
import sys
import os

from imapfw.concurrency.concurrency import Concurrency
from imapfw.rascal import Rascal
from imapfw.actions.syncaccounts import SyncAccounts

from imapfw.testing.nullui import NullUI


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

        ui = NullUI
        action = SyncAccounts()
        options = {'accounts': ['AccountA']}
        try:
            action.initialize(ui, self.multiprocessing, self.rascal, options)
            action.run()
        except Exception as e:
            action.exception(e)
        self.assertEqual(action.getExitCode(), 0)
