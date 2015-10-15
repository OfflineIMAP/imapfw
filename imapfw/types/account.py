


class Account(object):

    left = None
    right = None

    def getName(self):
        return self.__class__.__name__

    def sync_folders(self, folderList):
        return folderList
