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

from .engine import Engine

from ..types.account import Account
from ..constants import WRK


    #def exposed_startFolderWorkers(self, syncfolders, maxFolderWorkers,
        #accountName):

        #self.ui.debugC(WRK, "creating the folders workers for %s"% accountName)

        #self._foldersArchitect = FoldersArchitect(accountName)
        ## Build the required child workers.
        #self._foldersArchitect.start(syncfolders, maxFolderWorkers)

class SyncAccount(Engine):
    """The sync account engine.

    Used by the account manager."""

    def __init__(self, workerName, leftEmitter, rightEmitter):
        self._workerName = workerName
        self._left = leftEmitter
        self._rght = rightEmitter

        self.ui = runtime.ui
        self.rascal = runtime.rascal

        self._accountName = None
        self._leftFolders = None
        self._rghtFolders = None
        self._maxFolderWorkers = None
        self._runResults = None, None, None

        # Define the flow of actions.
        self._left.getFolders.addOnSuccess(self._onLeftGetFolders)
        self._left.getFolders.addOnSuccess(self._mergeFolders)
        self._rght.getFolders.addOnSuccess(self._onRghtGetFolders)
        self._left.getFolders.addOnSuccess(self._mergeFolders)

    def _onLeftGetFolders(self, folders):
        self._leftFolders = folders

    def _onRghtGetFolders(self, folders):
        self._rghtFolders = folders

    def _mergeFolders(self, _):
        if None in [self._leftFolders, self._rghtFolders]:
            return

        # Merge the folder lists.
        mergedFolders = []
        for sideFolders in [self._leftFolders, self._rghtFolders]:
            for folder in sideFolders:
                if folder not in mergedFolders:
                    mergedFolders.append(folder)

        self.ui.infoL(3, "%s merged folders %s"%
            (self._accountName, mergedFolders))

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
            self._runResults = None, None, None
            return # Nothing more to do, stop here.

        self.ui.infoL(3, "%s syncing folders %s"%
            (self._accountName, syncFolders))

        #TODO: make max_connections mandatory.
        maxFolderWorkers = min(len(syncFolders), self._maxFolderWorkers)

        self._runResults = syncFolders, maxFolderWorkers, self._accountName

    def _run(self, accountName):
        # Get the account instance from the rascal.
        self._account = self.rascal.get(accountName, [Account])
        # Get the repository instances from the rascal.
        leftRepository, rghtRepository = self.getRepositories(
            self._account, self.rascal)

        self._maxFolderWorkers = min(
            rghtRepository.conf.get('max_connections'),
            leftRepository.conf.get('max_connections'))

        self._left.buildDriver(leftRepository.getName())
        self._rght.buildDriver(rghtRepository.getName())

        # Connect the drivers.
        self._left.connect()
        self._rght.connect()

        # Get the folders from both sides so we can feed the folder tasks.
        self._left.getFolders()
        self._rght.getFolders()

        # Disable the emitters since we don't need them anymore.
        self._left.disable()
        self._rght.disable()

    def getResults(self):
        return self._runResults

    def run(self, accountName):
        self._accountName = accountName

        try:
            self.ui.infoL(2, "syncing %s"% self._accountName)
            self._run()
            self.ui.infoL(3, "syncing %s done"% self._accountName)
        except Exception:
            self.ui.error("could not sync account %s"% self._accountName)
            raise

