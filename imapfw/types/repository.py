

class RepositoryInterface(object):
    conf = None
    driver = None

    def getClassName(self):
        raise NotImplementedError


class RepositoryBase(RepositoryInterface):
    conf = None
    driver = None

    def getClassName(self):
        return self.__class__.__name__
