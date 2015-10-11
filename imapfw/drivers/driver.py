
class DriverInterface(object):
    def connect(self):
        raise NotImplementedError

    def getClassName(self):
        raise NotImplementedError

    def getFolders(self):
        raise NotImplementedError


class DriverBase(DriverInterface):
    def getClassName(self):
        return self.__class__.__name__
