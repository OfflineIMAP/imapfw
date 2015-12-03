# The MIT License (MIT).
# Copyright (c) 2015, Nicolas Sebrecht & contributors.

"""

Working with accounts implies end-to-end connections.  Each end is a driver to
work with the data. The engine holds the algorithm, it is put "in the middle".

SCHEMATIC OVERVIEW
------------------

```

  {worker}                        {worker}                         {worker}
+----------+                    +----------+                     +----------+
|          |      (drives)      |          |      (drives)       |          |
|  driver  |<-------------------|  engine  +-------------------->|  driver  |
|          |                    |          |                     |          |
+----------+                    +----------+                     +----------+

```
"""

from imapfw import runtime
from imapfw.engines import SyncAccounts
from imapfw.runners import topRunner
from imapfw.edmp import newEmitterReceiver

from .architect import EngineArchitect
from .folder import SyncFoldersArchitect
from .debug import debugArchitect

# Annotations.
from imapfw.annotation import Iterable
from imapfw.edmp import Queue
from imapfw.types.folder import Folders


@debugArchitect
class SyncArchitect(object):
    def __init__(self, workerName: str, accountTasks: Queue,
            accountEngineName: str, folderEngineName: str):
        self.workerName = workerName
        self.accountTasks = accountTasks
        self.accountEngineName = accountEngineName
        self.folderEngineName = folderEngineName

        self.engineArch = None
        self.foldersArch = None
        self.receiver = None
        self.engine = None
        self.exitCode = -1 # Let caller know we are busy.
        self.foldersExitCode = -1
        # Let the account engine know when folders are done.
        self.runnerShouldWait = True

    # def _on_running(self) -> None:
        # """The runner let us know when processing an new task.

        # We don't wait for syncFolders event to be triggered to avoid race
        # conditions."""

        # self.runnerShouldWait = True

    def _on_stop(self, exitCode: int) -> None:
        """React to `done` event.

        This event is triggered when the sync engine has no more task to
        process. Stop worker and set exit code."""

        self.runnerShouldWait = False
        if self.foldersArch is not None:
            self._setExitCode(self.foldersArch.getExitCode())
        self.engineArch.stop()
        self._setExitCode(exitCode)
        self._setExitCode(self.foldersExitCode)

    def _on_syncFolders(self, accountName: str, maxFolderWorkers: int,
            folders: Folders) -> None:
        """Start syncing of folders in async mode."""

        self.foldersArch = SyncFoldersArchitect(self.workerName, accountName)
        # Let the foldersArchitect re-use our drivers.
        self.foldersArch.start(
            maxFolderWorkers,
            folders,
            self.engineArch.getLeftEmitter(),
            self.engineArch.getRightEmitter(),
            )

    def _on_areFoldersDone(self) -> bool:
        """The runner will request us to know if folder workers are all done.

        The account is fully processed once the folders are synced. The engine
        must not monitor for this flag if there's no folder workers to run (no
        syncFolders event).
        """

        return self.runnerShouldWait

    def _setExitCode(self, exitCode: int) -> None:
        if exitCode > self.exitCode:
            self.exitCode = exitCode

    def init(self) -> None:
        """Initialize the architect. Helps to compose components easily."""
        self.engineArch = EngineArchitect(self.workerName)
        self.engineArch.init()

        self.receiver, emitter = newEmitterReceiver(self.workerName)

        # Setup events handling.
        # self.receiver.accept('running', self._on_running)
        self.receiver.accept('stop', self._on_stop)
        self.receiver.accept('syncFolders', self._on_syncFolders)
        self.receiver.accept('areFoldersDone', self._on_areFoldersDone)

        self.engine = SyncAccounts(
            self.workerName,
            emitter,
            self.engineArch.getLeftEmitter(),
            self.engineArch.getRightEmitter(),
            )

    def getExitCode(self) -> int:
        """Caller must monitor the exit code to know when we are done.

        - negative: busy.
        - zero: finished without error.
        - positive: got unrecoverable error."""

        try:
            self.receiver.react()
            if self.foldersArch is not None:
                exitCode = self.foldersArch.getExitCode()
                if exitCode >= 0:
                    # Folders are all done.
                    self.runnerShouldWait = False
                    self.foldersExitCode = exitCode
                    self.foldersArch = None

        except Exception as e:
            #TODO: honor rascal.
            runtime.ui.critical("%s got unexpected error '%s'"%
                    (self.workerName, e))
            runtime.ui.exception(e)
            # Stop here.
            self.engineArch.kill()
            if self.foldersArch is not None:
                self.foldersArch.kill()
            self._setExitCode(10) # See manual.

        return self.exitCode

    def start(self) -> None:
        assert self.engineArch is not None

        self.engineArch.start(
            topRunner,
            (self.workerName, self.engine.run, self.accountTasks),
            )


class SyncAccountsArchitect(object):
    """Architect to sync accounts."""

    def __init__(self, accountList: Iterable[str]):
        self.accountList = accountList

        self.syncArchs = [] # Collection of SyncAccountsArchitect.
        self.exitCode = -1
        self.accountTasks = None

    def start(self, maxConcurrentAccounts: int) -> None:
        # The account names are the tasks for the account workers.
        accountTasks = runtime.concurrency.createQueue()
        for name in self.accountList:
            accountTasks.put(name)

        # Avoid race condition: an empty would let account workers to quit
        # without processing the content. We have to make sure the queue is not
        # empty before they start. accountList can't be empty as defined by the
        # argument parser.
        while accountTasks.empty():
            pass
        # Oops! This is still racy! This assumes that the NEXT task is available
        # once the previous run is done. This should be reasonable assumption,
        # though...

        # Setup the architecture.
        for i in range(maxConcurrentAccounts):
            workerName = "Account.%i"% i

            syncArch = SyncArchitect(workerName, accountTasks,
                    'SyncAccountEngine', 'SyncFolderEngine')
            syncArch.init()
            syncArch.start() # Async.
            self.syncArchs.append(syncArch)

    def run(self) -> int:
        # Monitor the architects.
        while len(self.syncArchs) > 0:
            for architect in self.syncArchs:
                exitCode = architect.getExitCode()
                if exitCode >= 0:
                    if exitCode > self.exitCode:
                        self.exitCode = exitCode
                    self.syncArchs.remove(architect)

        if self.exitCode < 0:
            return 99 # See manual.
        return self.exitCode
