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


"""

The Account Manager will always start both side drivers.

"""

from imapfw import runtime

from .manager import Manager

from ..architects.folder import FoldersArchitect
from ..constants import WRK


class AccountManager(Manager):
    """The account manager of an architect with both sides drivers.

    This does NOT defines what the worker actually does since this is the purpose
    of the engines.

    All the code of this object is run into the main worker."""

    def __init__(self, workerName):
        super(AccountManager, self).__init__()

        self._workerName = workerName

        self._rascal = runtime.rascal
        self._foldersArchitect = None

    def exposed_killFolderWorkers(self):
        return self._foldersArchitect.killAll()

    def exposed_serve_next(self):
        return self._foldersArchitect.serveAll()

    def exposed_startFolderWorkers(self, syncfolders, maxFolderWorkers,
        accountName):

        self.ui.debugC(WRK, "creating the folders workers for %s"% accountName)

        self._foldersArchitect = FoldersArchitect(accountName)
        # Build the required child workers.
        self._foldersArchitect.start(syncfolders, maxFolderWorkers)
