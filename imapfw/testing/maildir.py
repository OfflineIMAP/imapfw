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
import os

from imapfw import runtime
from imapfw.api import drivers
from imapfw.drivers.driver import loadDriver
from imapfw.testing import libcore
from imapfw.testing.nullui import NullUI
from imapfw.types.folder import Folders, Folder


class TestMaildirDriver(unittest.TestCase):
    def setUp(self):
        runtime.set_module('ui', NullUI)

        confBase = { 'sep': '/' }
        confA, confB = confBase.copy(), confBase.copy()

        confA['path'] = os.path.join(libcore.testingPath(), 'maildirs', 'recursive_A')
        confB['path'] = os.path.join(libcore.testingPath(), 'maildirs', 'recursive_B')

        self.driverA = loadDriver(drivers.Maildir, 'MaildirA', confA)
        self.driverB = loadDriver(drivers.Maildir, 'MaildirB', confB)

    def test_getFolders_of_recursive_A(self):
        folders = self.driverA.getFolders()
        expected = Folders(Folder(b'/'))
        self.assertEqual(folders, expected)

    def test_getFolders_of_recursive_B(self):
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
