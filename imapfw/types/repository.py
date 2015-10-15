

class RepositoryInterface(object):
    conf = None
    driver = None

    def getName(self):
        raise NotImplementedError


class RepositoryBase(RepositoryInterface):
    conf = None
    driver = None

    def getName(self):
        return self.__class__.__name__
