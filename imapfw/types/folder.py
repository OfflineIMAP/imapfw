
from collections import UserList
from functools import total_ordering


class FolderInternalInterface(object):
    pass #TODO


class FolderInterface(FolderInternalInterface):
    def getName(self):              raise NotImplementedError
    def setName(self, name):        raise NotImplementedError


@total_ordering
class Folder(FolderInterface):
    """Internal model representative of a folder.

    Used by any driver, controller or engine. Might be passed to the user via the
    rascal.

    Internal name is the folder name with the levels of hierarchy, type bytes.

    Each driver must use the same representation so that a folder from a driver
    can be compared to a folder from another driver.
    """

    def __init__(self, name, encoding=None):
        self._name = None
        self.setName(name, encoding)

    def __bytes__(self):
        return self._name

    def __eq__(self, other):
        return self.getName() == other.getName()

    def __lt__(self, other):
        return self.getName() < other.getName()

    def __repr__(self):
        return repr(self._name.decode('UTF-8'))

    def __str__(self):
        return self.getName()

    def getName(self, encoding='UTF-8'):
        return self._name.decode(encoding)

    def setName(self, name, encoding=None):
        """Set the name of the folder.

        :name: folder name with hierarchy seperated by '/' (e.g.
        'a/folder').
        :encoding: encoding of the name. Expects bytes if not set.
        """

        if type(name) == bytes:
            self._name = name
        else:
            self._name = name.encode(encoding)


class Folders(UserList):
    """A list of Folder instances."""

    def __init__(self, *args):
        self.data = list(args)
