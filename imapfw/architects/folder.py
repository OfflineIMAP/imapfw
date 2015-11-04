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
from imapfw.runners import topRunner
from imapfw.engines import SyncFolders

from .driver import DriverArchitect

# Annotations.
from imapfw.edmp import Emitter
from imapfw.concurrency import Queue
from imapfw.types.folder import Folders


class FolderArchitectInterface(object):
    def getExitCode(self):  raise NotImplementedError
    def kill(self):         raise NotImplementedError
    def start(self):        raise NotImplementedError


class FolderArchitect(FolderArchitectInterface):
    """The agent is run in the worker."""

    def __init__(self, workerName, accountName: str):
        self._workerName = workerName
        self._accountName = accountName

        self._debug("__init__(%s, %s)"% (workerName, accountName))

        self._worker = None
        self._receiver = None
        self._leftArchitect = None
        self._rightArchitect = None
        self._exitCode = -1

    def _debug(self, msg):
        runtime.ui.debugC(ARC, "%s folderArchitect %s"% (self._workerName, msg))

    def _setExitCode(self, exitCode: int):
        self._debug("_setExitCode(%i)"% exitCode)
        if exitCode > self._exitCode:
            self._exitCode = exitCode

    def _stop(self, exitCode: int):
        self._debug("stop(%i)"% exitCode)
        for architect in [self._leftArchitect, self._rightArchitect]:
            if architect is not None:
                architect.stop()
        self._worker.join()
        self._setExitCode(exitCode)

    def kill(self):
        self._debug("kill()")
        for architect in [self._leftArchitect, self._rightArchitect]:
            if architect is not None:
                architect.kill()
        self._worker.kill()

    def getExitCode(self):
        try:
            self._receiver.react()
        except Exception as e:
            runtime.ui.critical("folder receiver [%s] got unexpected error: %s"%
                (self._worker.getName(), e))
            runtime.ui.exception(e)
            self.kill()
            self._setExitCode(10)
        return self._exitCode

    def start(self, folderTasks: Queue, left: Emitter, right: Emitter):
        self._debug("start()")

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

        receiver, emitter = newEmitterReceiver(self._workerName)
        receiver.accept('stop', self._stop)
        self._receiver = receiver

        #TODO: the architect must not know what engine will be used.
        # 'SyncFolder' from rascal: review Account.engine.
        engine = SyncFolders(self._workerName, emitter, left, right,
            self._accountName)

        self._worker = runtime.concurrency.createWorker(
            self._workerName,
            topRunner,
            (self._workerName, engine.syncFolders, folderTasks),
            )

        self._worker.start()


class FoldersArchitectInterface(object):
    def getExitCode(self):  raise NotImplementedError
    def kill(self):         raise NotImplementedError
    def start(self):        raise NotImplementedError


class FoldersArchitect(FoldersArchitectInterface):
    """Handle a collection of FolderArchitect instances.

    Can be used in a per-account basis."""

    def __init__(self, callerName: str, accountName: str):
        self._accountName = accountName
        self._callerName = callerName

        self._folderArchitects = []
        self._exitCode = -1


    def _debug(self, msg):
        runtime.ui.debugC(ARC, "%s foldersArchitect %s %s"%
            (self._callerName, self._accountName, msg))

    def _setExitCode(self, exitCode):
        self._debug("_setExitCode(%i)"% exitCode)
        if exitCode > self._exitCode:
            self._exitCode = exitCode

    def getExitCode(self):
        for folderArchitect in self._folderArchitects:
            exitCode = folderArchitect.getExitCode()
            if exitCode >= 0:
                self._folderArchitects.remove(folderArchitect)
                self._setExitCode(exitCode)
                self._debug("%i architect(s) remaining"%
                    len(self._folderArchitects))

        if len(self._folderArchitects) < 1:
            return self._exitCode
        else:
            return -1 # Let caller know workers are busy.

    def kill(self):
        self._debug("kill()")
        for folderArchitect in self._folderArchitects:
            folderArchitect.kill()
            self._folderArchitects.remove(folderArchitect)

    def start(self, maxFolderWorkers: int, folders: Folders,
            left: Emitter=None, right: Emitter=None):

        self._debug("start(%i, %s, %s, %s)"% (maxFolderWorkers,
            folders, repr(left), repr(right)))

        folderTasks = runtime.concurrency.createQueue()
        for folder in folders:
            folderTasks.put(folder)
        # Avoid race conditions. See actions.syncaccounts.
        while folderTasks.empty():
            pass

        for i in range(maxFolderWorkers):
            workerName = "%s.Folder.%i"% (self._callerName, i)

            folderArchitect = FolderArchitect(workerName, self._accountName)
            folderArchitect.start(folderTasks, left, right)
            left, right = None, None # Don't re-use drivers too much. :-)
            self._folderArchitects.append(folderArchitect)
