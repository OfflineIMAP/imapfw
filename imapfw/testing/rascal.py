# The MIT License (MIT).
# Copyright (c) 2015, Nicolas Sebrecht & contributors.

import unittest
import os

from imapfw.rascal import Rascal
from imapfw.api import types
from imapfw.testing import libcore


class TestRascal(unittest.TestCase):
    def setUp(self):
        def loadRascal(path):
            rascal = Rascal()
            rascal.load(path)
            return rascal

        rascalsDir = os.path.join(
            libcore.testingPath(),
            'rascals',
            )

        self.rascal = loadRascal(os.path.join(rascalsDir, 'basic.rascal'))
        self.empty = loadRascal(os.path.join(rascalsDir, 'empty.rascal'))

    def test_getAccountA(self):
        cls_account = self.rascal.get('AccountA', [types.Account])
        self.assertIsInstance(cls_account(), types.Account)

    def test_getExceptionHook(self):
        self.assertEqual(type(self.rascal.getExceptionHook()), type(lambda x:x))

    def test_getExceptionHookEmpty(self):
        self.assertTrue(callable(self.empty.getExceptionHook()))

    def test_getMaxConnections(self):
        self.assertEqual(self.rascal.getMaxConnections('AccountA'), 9)

    def test_getMaxSyncAccounts(self):
        self.assertEqual(self.rascal.getMaxSyncAccounts(), 7)

    def test_getPostHook(self):
        self.assertEqual(type(self.rascal.getPostHook()), type(lambda x:x))

    def test_getPostHookEmpty(self):
        self.assertEqual(type(self.empty.getPostHook()), type(lambda x:x))

    def test_runPreHook(self):
        from imapfw.toolkit import runHook

        stop = runHook(self.rascal.getPreHook(), 'actionName', {'action': 'actionName'})
        self.assertFalse(stop)

    def test_runPreHookEmpty(self):
        from imapfw.toolkit import runHook

        stop = runHook(self.rascal.getPreHook(), 'actionName', {'action': 'actionName'})
        self.assertFalse(stop)


if __name__ == '__main__':
    unittest.main(verbosity=2)
