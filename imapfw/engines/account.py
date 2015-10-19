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

import traceback

from imapfw import runtime

from .engine import Engine

from ..types.account import Account
from ..constants import WRK


class SyncAccount(Engine):
    """The sync account engine.

    Designed to be used by the generic ConsummerRunner. Consumes account names,
    one by one.

    Prepare the environement inside the worker and run the engine.
    """

    def __init__(self, workerName, tasks, accountEmitter, leftEmitter, rightEmitter):
        self._workerName = workerName
        self._tasks = tasks
        self._accountEmitter = accountEmitter
        self._left = leftEmitter  # Control the left driver (emitter).
        self._rght = rightEmitter # Control the right driver (emitter).

        self.ui = runtime.ui
        self.rascal = runtime.rascal

    def _consume(self, accountName):
        account = self.rascal.get(accountName, [Account])
        leftRepository, rghtRepository = self.getRepositories(
            account, self.rascal)

        self._left.buildDriver(leftRepository.getName(), _nowait=True)
        self._rght.buildDriver(rghtRepository.getName(), _nowait=True)

        # Connect the drivers.
        self._left.connect(_nowait=True)
        self._rght.connect(_nowait=True)

        # Fetch folders concurrently.
        self._left.fetchFolders(_nowait=True)
        self._rght.fetchFolders(_nowait=True)

        # Get the folders from both sides so we can feed the folder tasks.
        leftFolders = self._left.getFolders()
        rghtFolders = self._rght.getFolders()

        # Free the connections since we don't need them anymore.
        self._left.logout(_nowait=True)
        self._rght.logout(_nowait=True)

        # Merge the folder lists.
        mergedFolders = []
        for sideFolders in [leftFolders, rghtFolders]:
            for folder in sideFolders:
                if folder not in mergedFolders:
                    mergedFolders.append(folder)
        self.ui.infoL(3, "%s merged folders %s"% (accountName, mergedFolders))

        # Pass the list to the rascal.
        rascalFolders = account.syncFolders(mergedFolders)

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
                " for '%s': %s", account.getName(), ignoredFolders)

        if len(syncFolders) < 1:
            return # Nothing to do, stop here.
        self.ui.infoL(3, "%s syncing folders %s"% (accountName, syncFolders))

        #TODO: make max_connections mandatory.
        maxFolderWorkers = min(
            len(syncFolders),
            rghtRepository.conf.get('max_connections'),
            leftRepository.conf.get('max_connections'))

        # Start the folder workers.
        self._accountEmitter.startFolderWorkers(
            syncFolders, maxFolderWorkers, accountName)

        # Blok until all folders are synced. The loop must stand here because:
        # - we don't want to block the main worker while syncing this lone account;
        # - we don't need extra machinery to get notified when the work is done.
        while self._accountEmitter.serve_next():
            pass

    def run(self):
        try:
            while True:
                task =  self._tasks.get_nowait()
                if task is None: # No more task.
                    break # Quit the consumer loop.

                self.ui.infoL(2, "syncing %s"% task)
                self._consume(task)
                self.ui.infoL(3, "syncing %s done"% task)

            self._left.stopServing()
            self._rght.stopServing()
            self._accountEmitter.stopServing()
            self.ui.debugC(WRK, "runner ended")
        except Exception as e:
            self.ui.error('%s exception occured: %s\n%s', self._workerName, e,
                traceback.format_exc())
            # In threading: will send logout() to drivers from driver architect.
            # In multiprocessing: will send SIGTERM.
            self._accountEmitter.interruptionError(e.__class__, str(e))
