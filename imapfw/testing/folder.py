
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
