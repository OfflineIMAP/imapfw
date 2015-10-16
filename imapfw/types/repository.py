

class RepositoryIntenalInterface(object):
    def fw_init(self): raise NotImplementedError


class RepositoryInterface(RepositoryIntenalInterface):
    conf = None
    driver = None
    isLocal = None

    def fetchFolders(self): raise NotImplementedError
    def getName(self):      raise NotImplementedError
    def getFolders(self):   raise NotImplementedError


class RepositoryBase(RepositoryInterface):
    conf = None
    driver = None

    def fw_init(self, controller):
        self.controller = controller

    def fetchFolders(self):
        return self.controller.fetchFolders()

    def getFolders(self):
        return self.controller.getFolders()

    def getName(self):
        return self.__class__.__name__
