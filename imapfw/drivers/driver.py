
class DriverInterface(object):
    def connect(self):
        raise NotImplementedError

    def getFolders(self):
        raise NotImplementedError
