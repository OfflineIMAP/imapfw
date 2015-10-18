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

from imapfw import runtime

from ..types.account import Account
from ..types.repository import RepositoryBase
#from ..constants import CTL


class AccountTaskRunnerInterface(object):
    def getTask(self): raise NotImplementedError
    def consume(self): raise NotImplementedError


class SyncAccount(AccountTaskRunnerInterface):
    """The runner to consume account names, one by one.

    Designed to be used by the generic ConsummerRunner.

    Prepare the environement inside the worker and run the engine.
    """

    def __init__(self, tasks, accountEmitter, leftEmitter, rightEmitter):
        self._tasks = tasks
        self._accountEmitter = accountEmitter
        self._left = leftEmitter  # Control the left driver (emitter).
        self._rght = rightEmitter # Control the right driver (emitter).

        self.ui = runtime.ui
        self.rascal = runtime.rascal
        self._engine = None
        self._account = None


    def getTask(self):
        return self._tasks.getTask()

    def consume(self, accountName):
        """The runner for syncing an account in a worker.

        :accountName: the account name to sync.
        """

        #
        # Really start here.
        #
        self.ui.infoL(2, "syncing %s"% accountName)

        self._account = self.rascal.get(accountName, [Account])
        leftRepository = self.rascal.get(
            self._account.left.__name__, [RepositoryBase])
        rghtRepository = self.rascal.get(
            self._account.right.__name__, [RepositoryBase])

        self._left.buildDriverForRepository(leftRepository.getName())
        self._rght.buildDriverForRepository(rghtRepository.getName())

        # Connect the drivers.
        self._left.connect()
        self._rght.connect()

        # Initialize the repository instances.
        leftRepository.fw_init()
        rghtRepository.fw_init()

        # Fetch folders concurrently.
        self._left.fetchFolders()
        self._rght.fetchFolders()

        # Get the folders from both sides so we can feed the folder tasks.
        leftFolders = self._left.getFolders()
        rghtFolders = self._rght.getFolders()

        # Merge the folder lists.
        mergedFolders = []
        for sideFolders in [leftFolders, rghtFolders]:
            for folder in sideFolders:
                if folder not in mergedFolders:
                    mergedFolders.append(folder)

        # Pass the list to the rascal.
        rascalFolders = self._account.syncFolders(mergedFolders)

        # The rascal might request for non-existing folders!
        syncFolders = []
        ignoredFolders = []
        for folder in rascalFolders:
            if folder in mergedFolders:
                syncFolders.append(folder)
            else:
                ignoredFolders.append(folder)

        if len(ignoredFolders) > 0:
            self.ui.warn("rascal, you asked to sync non-existing folders"
                " for '%s': %s", self._account.getName(), ignoredFolders)

        if len(syncFolders) < 1:
            self._continue = False # Nothing to do, stop here.

        self._syncFolders = syncFolders
        self._continue = True

        ## Feed the folder tasks.
        #self._accountEmitter.startFolderWorkers(accountName, syncFolders)
        ## Block until all the folders are synced.
        #self._accountEmitter.serveFolderWorkers()

        #TODO: move out.
        # Leave the driver in Authenticated state.
        self._left.logout()
        self._rght.logout()

        self._left.stopServing()
        self._rght.stopServing()

        self.ui.infoL(3, "syncing %s done"% accountName)
