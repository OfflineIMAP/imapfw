
class AccountInterface(object):
    def getFolders(self, driver):   raise NotImplementedError
    def getName(self):              raise NotImplementedError


class Account(AccountInterface):

    left = None
    right = None

    def getName(self):
        return self.__class__.__name__

    def syncFolders(self, folderList):
        return folderList
