

class DriverInternalInterface(object):
    """Users must NOT change those methods."""

    def fw_initialize(self, ui, conf, owner):  raise NotImplementedError
    def fw_sanityChecks(self):          raise NotImplementedError


class DriverInterface(DriverInternalInterface):

    conf = {} # The configuration of the type has to be there.

    def connect(self):      raise NotImplementedError
    def getFolders(self):   raise NotImplementedError
    def getName(self):      raise NotImplementedError
    def logout(self):       raise NotImplementedError


class DriverBase(DriverInterface):
    def fw_initialize(self, ui, conf, owner):
        self.ui = ui
        self.conf = conf # Comes from the type.
        self.owner = owner

    @staticmethod
    def fw_sanityChecks(inst):
        if not isinstance(inst, DriverInterface):
            raise Exception("driver class %s does not satisfy DriverInterface"%
                inst.__class__.__name__)

    def getName(self):
        return self.__class__.__name__

    def getOwner(self):
        return self.owner
