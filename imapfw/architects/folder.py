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

from imapfw.constants import ARC
from imapfw.edmp import newEmitterReceiver
from imapfw.runners import FolderRunner, topRunner

from .driver import DriverArchitect

# Annotations.
from imapfw.edmp import Emitter
from imapfw.concurrency import Queue
from imapfw.types.folder import Folders


class FolderArchitectInterface(object):
    def join(self):         raise NotImplementedError
    def kill(self):         raise NotImplementedError
    def serve_next(self):   raise NotImplementedError
    def start(self):        raise NotImplementedError


class FolderArchitect(FolderArchitectInterface):
    """The agent is run in the worker."""

    def __init__(self, workerName, accountName: str):
        self._workerName = workerName
        self._accountName = accountName

        self.ui = runtime.ui
        self.concurrency = runtime.concurrency
        self._worker = None
        self._receiver = None
        self._leftArchitect = None
        self._rightArchitect = None
        self._exitCode = -1

        self._debug("created")

    def _debug(self, msg):
        self.ui.debugC(ARC, "%s architect %s"% (self._workerName, msg))

    def _stop(self, exitCode: int):
        for architect in [self._leftArchitect, self._rightArchitect]:
            if architect is not None:
                architect.stop()
        self._worker.join()
        self._exitCode = exitCode

    def kill(self):
        self._debug("will be killed")
        self._worker.kill()

    def getExitCode(self):
        try:
            self._receiver.react()
        except Exception as e:
            #TODO: review
            self.ui.error("%s raised exception %s"%
                (self._worker.getName(), str(e)))
            self.ui.exception(e)
            self.kill()
        return self._exitCode

    def start(self, folderTasks: Queue, left: Emitter, right: Emitter):
        self._debug("starting")

        receiver, emitter = newEmitterReceiver(self._workerName)
        receiver.accept('stop', self._stop)
        self._receiver = receiver

        if left is None:
            self._leftArchitect = DriverArchitect(
                "%s.Driver.0"% self._workerName)
            self._leftArchitect.start()
            left = self._leftArchitect.getEmitter()
        if right is None:
            self._rightArchitect = DriverArchitect(
                "%s.Driver.1"% self._workerName)
            self._rightArchitect.start()
            right = self._rightArchitect.getEmitter()

        #TODO: SyncFolder from rascal.
        runner = FolderRunner(emitter, left, right, 'SyncFolder')

        self._worker = self.concurrency.createWorker(
            self._workerName,
            topRunner,
            (runner.run, self._workerName, folderTasks),
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

    def __init__(self, callerName: str, accountName: str):
        self._accountName = accountName
        self._callerName = callerName

        self.ui = runtime.ui
        self.concurrency = runtime.concurrency
        self._folderArchitects = []
        self._exitCode = -1

        self._debug('created')

    def _debug(self, msg):
        self.ui.debugC(ARC, "%s architect %s"%
            (self._accountName, msg))

    #TODO
    def _kill(self):
        for folderArchitect in self._folderArchitects:
            self._folderArchitects.remove(folderArchitect)
            folderArchitect.kill()

    def _setExitCode(self, exitCode):
        if exitCode > self._exitCode:
            self._exitCode = exitCode

    def getExitCode(self):
        for folderArchitect in self._folderArchitects:
            exitCode = folderArchitect.getExitCode()
            if exitCode >= 0:
                self._folderArchitects.remove(folderArchitect)
                self._setExitCode(exitCode)
        if len(self._folderArchitects) < 1:
            return self._exitCode
        else:
            return -1 # Let caller know workers are busy.

    def start(self, maxFolderWorkers: int, folders: Folders,
            left=None, right=None):
        self._debug("creating %i folder workers"% maxFolderWorkers)

        folderTasks = self.concurrency.createQueue()
        for folder in folders:
            folderTasks.put(folder)
        # Avoid being racy. See actions.syncaccounts.
        while folderTasks.empty():
            pass

        for i in range(maxFolderWorkers):
            workerName = "%s.Folder.%i"% (self._accountName, i)

            folderArchitect = FolderArchitect(workerName, self._accountName)
            folderArchitect.start(folderTasks, left, right)
            left, right = None, None # Don't re-use drivers too much. :-)
            self._folderArchitects.append(folderArchitect)
