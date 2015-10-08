
import unittest
import sys
import os

from imapfw.rascal.rascal import Rascal
from imapfw.api import types


class TestRascal(unittest.TestCase):
    def setUp(self):
        self.rascal = Rascal()
        imapfw_path = os.path.abspath(sys.modules['imapfw'].__path__[0])
        path = os.path.join(
            imapfw_path,
            'testing',
            'rascals',
            'basic.rascal'
            )
        self.rascal.load(path)

    def test_00_getConcurrencyBackendName(self):
        self.assertEqual(self.rascal.getConcurrencyBackendName(), 'multiprocessing')

    def test_01_getMaxSyncAccounts(self):
        self.assertEqual(self.rascal.getMaxSyncAccounts(), 7)

    def test_02_getAccountClass(self):
        self.assertIsInstance(self.rascal.getAccountClass('AccountA')(), types.Account)

    def test_03_getMaxConnections(self):
        self.assertEqual(self.rascal.getMaxConnections('AccountA'), 9)


if __name__ == '__main__':
    unittest.main(verbosity=2)
