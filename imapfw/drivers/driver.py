

class DriverInternalInterface(object):
    """Users must NOT change those methods."""

    def fw_initialize(self, ui, conf): raise NotImplementedError
    def fw_sanityChecks(self): raise NotImplementedError
    def fw_getName(self): raise NotImplementedError


class DriverInterface(DriverInternalInterface):

    conf = {} # The configuration of the type has to be there.

    def connect(self): raise NotImplementedError
    def getFolders(self): raise NotImplementedError
    def logout(self): raise NotImplementedError


class DriverBase(DriverInterface):
    def fw_initialize(self, ui, conf):
        self.ui = ui
        self.conf = conf # Comes from the type.

    def fw_getName(self):
        return self.__class__.__name__

    def fw_sanityChecks(self):
        if not isinstance(self, DriverInterface):
            raise Exception("driver class %s does not satisfy DriverInterface"%
                self.getName())
