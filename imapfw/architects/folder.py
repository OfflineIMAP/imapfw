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

from .driver import DriverArchitect

from ..mmp.folder import FolderManager
from ..engines.folder import SyncFolder
from ..constants import ARC


class FolderArchitectInterface(object):
    def join(self):         raise NotImplementedError
    def kill(self):         raise NotImplementedError
    def serve_next(self):   raise NotImplementedError
    def start(self):        raise NotImplementedError


class FolderArchitect(FolderArchitectInterface):
    """The agent is run in the worker."""

    def __init__(self, workerName, accountName):
        self._workerName = workerName
        self._accountName = accountName

        self.ui = runtime.ui
        self.concurrency = runtime.concurrency
        self._worker = None
        self._folderSink = None
        self._leftArchitect = None
        self._rightArchitect = None

        self._debug("created")

    def _debug(self, msg):
        self.ui.debugC(ARC, "%s architect %s"% (self._workerName, msg))

    def join(self):
        self._debug("will join")
        self._worker.join()

    def kill(self):
        self._debug("will be killed")
        self._worker.kill()

    def serve_next(self):
        try:
            return self._folderSink.serve_next()
        except Exception as e:
            self.ui.error("%s raised exception %s"%
                (self._worker.getName(), str(e)))
            self.kill()
        return False

    def start(self, folderTasks):
        self._debug("starting")

        folderManager = FolderManager()
        self._folderSink, folderAgent = folderManager.split()

        self._leftArchitect = DriverArchitect("%s.Driver.0"% self._workerName)
        self._rightArchitect = DriverArchitect("%s.Driver.1"% self._workerName)

        self._leftArchitect.start(folderAgent)
        self._rightArchitect.start(folderAgent)

        syncFolder = SyncFolder(
            self._workerName,
            folderTasks,
            self._leftArchitect.getAgent(),
            self._rightArchitect.getAgent(),
            self._accountName,
            folderAgent,
            )

        self._worker = self.concurrency.createWorker(
            self._workerName,
            syncFolder.run,
            (),
            )

        self._worker.start()


class FoldersArchitectInterface(object):
    def joinAll(self):      raise NotImplementedError
    def killAll(self):      raise NotImplementedError
    def start(self):        raise NotImplementedError
    def serveAll(self):     raise NotImplementedError


class FoldersArchitect(FoldersArchitectInterface):
    """Handle a collection of FolderArchitect instances.

    Can be used in a per-account basis."""

    def __init__(self, accountName):
        self._accountName = accountName

        self.ui = runtime.ui
        self.concurrency = runtime.concurrency
        self._folderArchitects = []

        self._debug('created')

    def _debug(self, msg):
        self.ui.debugC(ARC, "%s architect %s"%
            (self._accountName, msg))

    def killAll(self):
        for folderArchitect in self._folderArchitects:
            self._folderArchitects.remove(folderArchitect)
            folderArchitect.kill()

    def serveAll(self):
        for folderArchitect in self._folderArchitects:
            continueServing = folderArchitect.serve_next()
            if continueServing is False:
                self._folderArchitects.remove(folderArchitect)
                folderArchitect.join()
        return len(self._folderArchitects) < 1

    def start(self, syncFolders, maxFolderWorkers):
        self._debug("creating %i folder workers"% maxFolderWorkers)

        folderTasks = self.concurrency.createQueue()
        for syncFolder in syncFolders:
            folderTasks.put(syncFolder)

        while maxFolderWorkers > 0:
            maxFolderWorkers -= 1

            workerName = "Folder.Worker.%s.%i"% (
                self._accountName, maxFolderWorkers)

            folderArchitect = FolderArchitect(workerName, self._accountName)
            folderArchitect.start(folderTasks)
            self._folderArchitects.append(folderArchitect)
