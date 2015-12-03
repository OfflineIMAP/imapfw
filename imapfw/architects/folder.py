# The MIT License (MIT).
# Copyright (c) 2015, Nicolas Sebrecht & contributors.

from imapfw import runtime

from imapfw.constants import ARC
from imapfw.edmp import newEmitterReceiver
from imapfw.runners import topRunner
from imapfw.engines import SyncFolders

from .driver import DriverArchitect, ReuseDriverArchitect
from .architect import Architect

# Annotations.
from imapfw.edmp import Emitter
from imapfw.concurrency import Queue
from imapfw.types.folder import Folders


class SyncFolderArchitect(object):
    """The agent is run in the worker."""

    def __init__(self, workerName, accountName: str):
        self.workerName = workerName
        self.accountName = accountName

        self._debug("__init__(%s, %s)"% (workerName, accountName))

        self.worker = None
        self.receiver = None
        self.architect = None
        self.leftArch = None
        self.rightArch = None
        self.exitCode = -1

    def _debug(self, msg) -> None:
        runtime.ui.debugC(ARC, "%s folderArchitect %s"% (self.workerName, msg))

    def _on_stop(self, exitCode: int) -> None:
        self._debug("stop(%i)"% exitCode)

        self.leftArch.stop()
        self.rightArch.stop()
        self.architect.stop()
        self._setExitCode(exitCode)

    def _setExitCode(self, exitCode: int) -> None:
        self._debug("_setExitCode(%i)"% exitCode)
        if exitCode > self.exitCode:
            self.exitCode = exitCode

    def kill(self) -> None:
        self._debug("kill()")

        self.leftArch.stop()
        self.rightArch.stop()
        self.architect.kill()

    def getExitCode(self) -> int:
        try:
            self.receiver.react()
        except Exception as e:
            runtime.ui.critical("folder receiver [%s] got unexpected error: %s"%
                (self.workerName, e))
            runtime.ui.exception(e)
            self.kill()
            self._setExitCode(10) # See manual.
        return self.exitCode

    def start(self, folderTasks: Queue,
            left: Emitter, right: Emitter) -> None:

        self._debug("start()")

        self.architect = Architect(self.workerName)

        if left is None:
            self.leftArch = DriverArchitect("%s.Driver.0"% self.workerName)
            self.leftArch.init()
            self.leftArch.start()
            left = self.leftArch.getEmitter()
        else:
            self.leftArch = ReuseDriverArchitect(left)
        if right is None:
            self.rightArch = DriverArchitect("%s.Driver.1"% self.workerName)
            self.rightArch.init()
            self.rightArch.start()
            right = self.rightArch.getEmitter()
        else:
            self.rightArch = ReuseDriverArchitect(right)

        receiver, emitter = newEmitterReceiver(self.workerName)
        receiver.accept('stop', self._on_stop)
        self.receiver = receiver

        engine = SyncFolders(self.workerName, emitter, left, right,
            self.accountName)

        self.architect.start(
            topRunner,
            (self.workerName, engine.run, folderTasks),
            )


class SyncFoldersArchitect(object):
    """Handle a collection of FolderArchitect instances.

    Can be used in a per-account basis."""

    def __init__(self, accountWorkerName: str, accountName: str):
        self.accountName = accountName
        self.accountWorkerName = accountWorkerName

        self.folderArchitects = []
        self.exitCode = -1


    def _debug(self, msg) -> None:
        runtime.ui.debugC(ARC, "%s foldersArchitect %s %s"%
            (self.accountWorkerName, self.accountName, msg))

    def _setExitCode(self, exitCode) -> None:
        self._debug("_setExitCode(%i)"% exitCode)
        if exitCode > self.exitCode:
            self.exitCode = exitCode

    def getExitCode(self) -> int:
        for folderArchitect in self.folderArchitects:
            exitCode = folderArchitect.getExitCode()
            if exitCode >= 0:
                self.folderArchitects.remove(folderArchitect)
                self._setExitCode(exitCode)
                self._debug("%i architect(s) remaining"%
                    len(self.folderArchitects))

        if len(self.folderArchitects) < 1:
            return self.exitCode
        else:
            return -1 # Let caller know workers are busy.

    def kill(self) -> None:
        self._debug("kill()")
        for folderArchitect in self.folderArchitects:
            folderArchitect.kill()
            self.folderArchitects.remove(folderArchitect)

    def start(self, maxFolderWorkers: int, folders: Folders,
            left: Emitter=None, right: Emitter=None) -> None:

        self._debug("start(%i, %s, %s, %s)"% (maxFolderWorkers,
            folders, repr(left), repr(right)))

        folderTasks = runtime.concurrency.createQueue()
        for folder in folders:
            folderTasks.put(folder)
        # Avoid race conditions. See .account.SyncAccountsArchitect.
        while folderTasks.empty():
            pass

        for i in range(maxFolderWorkers):
            workerName = "%s.Folder.%i"% (self.accountWorkerName, i)

            folderArchitect = SyncFolderArchitect(workerName, self.accountName)
            folderArchitect.start(folderTasks, left, right)
            left, right = None, None # Don't re-use drivers too much. :-)
            self.folderArchitects.append(folderArchitect)
