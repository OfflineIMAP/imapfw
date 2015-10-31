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
from imapfw.types.folder import Folders

from .engine import Engine

# Annotations.
from imapfw.edmp import Emitter
from imapfw.types.account import Account


class SyncAccount(Engine):
    """The sync account engine.

    Used by the account runner."""

    def __init__(self, workerName: str, referent: Emitter,
            left: Emitter, right: Emitter):

        self._workerName = workerName
        self._referent = referent
        self._left = left
        self._rght = right

        self.ui = runtime.ui

        self._accountName = None
        self._leftFolders = None
        self._rghtFolders = None
        self._maxFolderWorkers = None
        self._exitCode = -1

    def _run(self, account):
        # Get the repository instances from the rascal.
        leftRepository, rghtRepository = self.getRepositories(account)

        self._left.buildDriver(leftRepository.getName())
        self._rght.buildDriver(rghtRepository.getName())

        # Connect the drivers.
        self._left.connect()
        self._rght.connect()

        self._left.fetchFolders()
        self._rght.fetchFolders()

        # Get the folders from both sides so we can feed the folder tasks.
        leftFolders = self._left.getFolders_sync()
        rghtFolders = self._rght.getFolders_sync()

        # Merge the folder lists.
        mergedFolders = Folders()
        for sideFolders in [leftFolders, rghtFolders]:
            for folder in sideFolders:
                if folder not in mergedFolders:
                    mergedFolders.append(folder)

        self.ui.infoL(3, "%s merged folders %s"%
            (self._accountName, mergedFolders))

        # Pass the list to the rascal.
        rascalFolders = account.syncFolders(mergedFolders)

        # The rascal might request for non-existing folders!
        syncFolders = Folders()
        ignoredFolders = Folders()
        for folder in rascalFolders:
            if folder in mergedFolders:
                syncFolders.append(folder)
            else:
                ignoredFolders.append(folder)

        if len(ignoredFolders) > 0:
            self.ui.warn("rascal, you asked to sync non-existing folders"
                " for '%s': %s", account.getName(), ignoredFolders)

        if len(syncFolders) < 1:
            self.ui.infoL(3, "%s: no folder to sync"% account)
            return # Nothing more to do.

        self.ui.infoL(3, "%s syncing folders %s"%
            (self._accountName, syncFolders))

        #XXX: make max_connections mandatory in rascal?
        maxFolderWorkers = min(
            len(syncFolders),
            rghtRepository.conf.get('max_connections'),
            leftRepository.conf.get('max_connections'))

        # Syncing folders is not the job of this engine.
        self._referent.syncFolders(self._accountName, maxFolderWorkers,
                syncFolders)

        self._exitCode = 0

    def run(self, account: Account):
        self._accountName = account.getName()

        try:
            self.ui.infoL(2, "syncing %s"% self._accountName)
            self._run(account)
            self.ui.infoL(3, "syncing %s done"% self._accountName)
            return self._exitCode
        except Exception:
            self.ui.error("could not sync account %s"% self._accountName)
            raise

