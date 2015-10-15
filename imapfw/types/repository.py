

class RepositoryInterface(object):
    conf = None
    driver = None

    def fetchFolders(self, driver): raise NotImplementedError
    def getName(self):              raise NotImplementedError
    def getFolders(self, driver):   raise NotImplementedError


class RepositoryBase(RepositoryInterface):
    conf = None
    driver = None

    def fetchFolders(self, driver):
        driver.fetchFolders_nowait()

    def getFolders(self, driver):
        return driver.getFolders()

    def getName(self):
        return self.__class__.__name__
