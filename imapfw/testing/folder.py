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

from imapfw.types.folder import Folders, Folder


class TestFolder(unittest.TestCase):
    def setUp(self):
        self.folderA = Folder(b'A')
        self.folderB = Folder(b'A')

        self.folderI = Folder(b'A/B')
        self.folderJ = Folder(b'A/B')

        self.foldersX = Folders(self.folderA, self.folderI)
        self.foldersY = Folders(self.folderB, self.folderJ)

    def test_folder_equal_one_level(self):
        self.assertEqual(self.folderA, self.folderB)

    def test_folder_equal_two_levels(self):
        self.assertEqual(self.folderI, self.folderJ)

    def test_folders_equal(self):
        self.assertEqual(self.foldersX, self.foldersY)


if __name__ == '__main__':
    unittest.main(verbosity=2)
