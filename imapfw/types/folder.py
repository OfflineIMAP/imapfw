# The MIT License (MIT)
#
# Copyright (c) 2015, Nicolas Sebrecht & contributors
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from collections import UserList
from functools import total_ordering

from imapfw.interface import implements, Interface, checkInterfaces

# Annotations.
from imapfw.annotation import Union


ENCODING = 'UTF-8'


class FolderInterface(Interface):
    """Internal model representative of a folder.

    Used by any driver, controller or engine. Might be passed to the user via the
    rascal.

    Internal name is the folder name with the levels of hierarchy, type bytes.

    Each driver must use the same representation so that a folder from a driver
    can be compared to a folder from another driver.
    """

    scope = Interface.PUBLIC

    def hasChildren(self) -> bool:
        """Return True of False whether this folder has children."""

    def getName(self, encoding: str=ENCODING) -> str:
        """Return folder base name."""

    def getRoot(self, encoding: str=ENCODING) -> str:
        """Return the path to the folder."""

    def setName(self, name: Union[str, bytes], encoding: str=None) -> None:
        """Set the folder base name."""

    def setHasChildren(self, hasChildren: bool) -> None:
        """Set if folder has children."""

    def setRoot(self, root: str, encoding: str=ENCODING) -> None:
        """Set the path to the folder."""


@total_ordering
@checkInterfaces()
@implements(FolderInterface)
class Folder(object):
    def __init__(self, name, encoding=None):
        self._name = None # Must be bytes.
        self.setName(name, encoding)

        self._hasChildren = None
        self._root = None

    def __bytes__(self):
        return self._name

    def __eq__(self, other):
        return self.getName() == other.getName()

    def __lt__(self, other):
        return self.getName() < other.getName()

    def __repr__(self):
        return repr(self._name.decode(ENCODING))

    def __str__(self):
        return self.getName()

    def getName(self, encoding: str=ENCODING) -> str:
        return self._name.decode(encoding)

    def getRoot(self, encoding: str=ENCODING) -> str:
        return self._root.decode(encoding)

    def hasChildren(self) -> bool:
        return self._hasChildren

    def setName(self, name: Union[str, bytes], encoding: str=None) -> None:
        """Set the name of the folder.

        :name: folder name with hierarchy seperated by '/' (e.g.
        'a/folder').
        :encoding: encoding of the name. Expects bytes if not set.
        """

        if type(name) == bytes:
            self._name = name
        else:
            self._name = name.encode(encoding)

    def setHasChildren(self, hasChildren: bool) -> None:
        self._hasChildren = hasChildren

    def setRoot(self, root: str, encoding: str=ENCODING) -> None:
        if type(root) == bytes:
            self._root = root
        else:
            self._root = root.encode(encoding)


class Folders(UserList):
    """A list of Folder instances."""

    def __init__(self, *args):
        super(Folders, self).__init__(list(args))
