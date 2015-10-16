
import unittest
import os

from imapfw.drivers.maildir import Maildir
from imapfw.testing import libcore
from imapfw.testing.nullui import NullUI
from imapfw.types.folder import Folders, Folder


class TestMaildirDriver(unittest.TestCase):
    def setUp(self):
        self.driverA, self.driverB = Maildir(), Maildir()

        confBase = { 'sep': '/' }
        confA, confB = confBase.copy(), confBase.copy()

        confA['path'] = os.path.join(libcore.testingPath(), 'maildirs', 'recursive_A')
        confB['path'] = os.path.join(libcore.testingPath(), 'maildirs', 'recursive_B')

        self.driverA.fw_initialize(NullUI(), confA, self.driverA)
        self.driverB.fw_initialize(NullUI(), confB, self.driverB)

    def test_getFolders_recursive_A(self):
        folders = self.driverA.getFolders()
        expected = Folders(Folder(b'/'))
        self.assertEqual(folders, expected)

    def test_getFolders_recursive_B(self):
        folders = self.driverB.getFolders()
        expected = Folders(
            Folder(b'/'),
            Folder(b'subfolder_A'),
            Folder(b'subfolder_B'),
            Folder(b'subfolder_B/subsubfolder_X'),
            )
        self.assertEqual(folders, expected)


if __name__ == '__main__':
    unittest.main(verbosity=2)
