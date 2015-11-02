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
from imapfw.runners import AccountRunner, topRunner

from .driver import DriverArchitect
from .folder import FoldersArchitect

# Annotations.
from imapfw.concurrency import Queue
from imapfw.types.folder import Folders


class AccountArchitectInterface(object):
    def getExitCode(self):  raise NotImplementedError
    def kill(self):         raise NotImplementedError
    def start(self):        raise NotImplementedError


class AccountArchitect(AccountArchitectInterface):
    """Handling an account with 2 end-drivers.

    Build, serve and destroy a link from end to end. Does not care what is done
    _within_ the link. This is the role of the engine which is put in the
    "middle"."""

    def __init__(self):
        self.ui = runtime.ui
        self.concurrency = runtime.concurrency

        self._leftArchitect = None
        self._rightArchitect = None
        self._receiver = None
        self._worker = None
        self._name = self.__class__.__name__
        self._folderExitCode = -1
        self._exitCode = -1 # Let the caller know that we are busy.
        self._accountRunnerWait = False
        self._foldersArchitect = None

    def _debug(self, msg):
        self.ui.debugC(ARC, "%s %s"% (self._name, msg))

    def _kill(self):
        self._debug("killing")
        self._accountRunnerWait = False
        self._leftArchitect.kill()
        self._rightArchitect.kill()
        self._worker.kill()

    def _running(self):
        """The runner let us know when processing an new account."""

        self._accountRunnerWait = True

    def _setFolderExitCode(self, exitCode):
        if exitCode > self._exitCode:
            self._folderExitCode = exitCode

    def _stop(self, exitCode: int):
        self._accountRunnerWait = False
        self._leftArchitect.stop()
        self._rightArchitect.stop()
        self._worker.join()
        self._exitCode = exitCode

    def _syncFolders(self, accountName: str, maxFolderWorkers: int,
            folders: Folders):
        """Start syncing of folders in async mode."""

        self.ui.infoL(3, "syncing folders: %s"% folders)
        self._foldersArchitect = FoldersArchitect(
            self._worker.getName(), accountName)
        # Let the foldersArchitect re-use our drivers.
        self._foldersArchitect.start(
            maxFolderWorkers,
            folders,
            self._leftArchitect.getEmitter(),
            self._rightArchitect.getEmitter(),
            )

    def _wait(self):
        return self._accountRunnerWait

    def getExitCode(self) -> int:
        """Caller must monitor the exit code to know when we are done.

        - negative: busy.
        - zero: finished without error.
        - positive: got unrecoverable error."""

        # Honor events from the worker.
        # Event handler will update the exit code when appropriate.
        try:
            self._receiver.react()
            if self._foldersArchitect is not None:
                exitCode = self._foldersArchitect.getExitCode()
                if exitCode >= 0:
                    self._foldersArchitect = None
                    self._setFolderExitCode(exitCode)
                    self._accountRunnerWait = False
        except Exception as e:
            self.ui.critical("account receiver for %s got unexpected error '%s'"%
                (self._name, e))
            self._kill()
        if self._exitCode >= 0:
            if self._folderExitCode > self._exitCode:
                self._exitCode = self._folderExitCode
        return self._exitCode

    def start(self, workerName: str, accountTasks: Queue, engineName: str):
        """Setup and initiate one account worker. Not blocking."""

        self._debug("starting start for '%s'"% workerName)

        # Setup and start both end-drivers.
        leftName, rightName = "%s.Driver.0"% workerName, "%s.Driver.1"% workerName
        self._leftArchitect = DriverArchitect(leftName)
        self._rightArchitect = DriverArchitect(rightName)

        self._leftArchitect.start()
        self._rightArchitect.start()

        # Setup events.
        receiver, emitter = newEmitterReceiver(workerName)
        receiver.accept('running', self._running)
        receiver.accept('stop', self._stop)
        receiver.accept('syncFolders', self._syncFolders)
        receiver.accept('wait', self._wait)
        self._receiver = receiver

        accountRunner = AccountRunner(
            emitter,
            self._leftArchitect.getEmitter(),
            self._rightArchitect.getEmitter(),
            engineName,
            )

        # Time for the worker.
        self._worker = self.concurrency.createWorker(workerName,
            topRunner,
            (accountRunner.run, workerName, accountTasks),
            )
        self._worker.start()
