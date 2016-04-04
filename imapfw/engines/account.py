# The MIT License (MIT).
# Copyright (c) 2015, Nicolas Sebrecht & contributors.

"""

Engines to work with accounts.

"""

from imapfw import runtime
from imapfw.edmp import Channel
from imapfw.types.folder import Folders
from imapfw.types.account import loadAccount

from .engine import SyncEngine, EngineInterface

# Interfaces.
from imapfw.interface import implements, checkInterfaces

# Annotations.
from imapfw.edmp import Emitter
from imapfw.concurrency import Queue
from imapfw.types.account import Account


@checkInterfaces()
@implements(EngineInterface)
class SyncAccounts(SyncEngine):
    """The sync account engine."""

    def __init__(self, workerName: str, referent: Emitter,
            left: Emitter, right: Emitter):
        super(SyncAccounts, self).__init__(workerName)

        self.referent = referent
        self.left = left
        self.rght = right

    # Outlined.
    def _syncAccount(self, account: Account):
        """Sync one account."""

        accountName = account.getClassName()

        runtime.ui.infoL(3, "merging folders for %s"% accountName)

        # Get the repository instances from the rascal.
        leftRepository = account.fw_getLeft()
        rghtRepository = account.fw_getRight()

        self.left.buildDriver(accountName, 'left')
        self.rght.buildDriver(accountName, 'right')

        # Connect the drivers.
        self.left.connect()
        self.rght.connect()

        self.left.getFolders()
        self.rght.getFolders()

        # Get the folders from both sides so we can feed the folder tasks.
        leftFolders = self.left.getFolders_sync()
        rghtFolders = self.rght.getFolders_sync()

        # Merge the folder lists.
        mergedFolders = Folders()
        for sideFolders in [leftFolders, rghtFolders]:
            for folder in sideFolders:
                if folder not in mergedFolders:
                    mergedFolders.append(folder)

        runtime.ui.infoL(3, "%s merged folders %s"%
            (accountName, mergedFolders))

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
            runtime.ui.warn("rascal, you asked to sync non-existing folders"
                " for '%s': %s", accountName, ignoredFolders)

        if len(syncFolders) < 1:
            runtime.ui.infoL(3, "%s: no folder to sync"% accountName)
            return # Nothing more to do.

        #TODO: make max_connections mandatory in rascal.
        maxFolderWorkers = min(
            len(syncFolders),
            rghtRepository.conf.get('max_connections'),
            leftRepository.conf.get('max_connections'))

        runtime.ui.infoL(3, "%s syncing folders %s"% (accountName, syncFolders))

        # Syncing folders is not the job of this engine. Use sync mode to ensure
        # the referent starts syncing of folders before this engine stops.
        self.referent.syncFolders_sync(
            accountName, maxFolderWorkers, syncFolders)

    def run(self, taskQueue: Queue) -> None:
        """Sequentially process the accounts."""

        #
        # Loop over the available account names.
        #
        for accountName in Channel(taskQueue):
            self.processing(accountName)

            # The syncer will let expode errors it can't recover from.
            try:
                # Get the account instance from the rascal.
                account = loadAccount(accountName)
                self._syncAccount(account)
                self.setExitCode(0)

            except Exception as e:
                runtime.ui.error("could not sync account %s"% accountName)
                runtime.ui.exception(e)
                #TODO: honor hook!
                self.setExitCode(10) # See manual.

        self.checkExitCode() # Sanity check.
        self.referent.accountEngineDone(self.getExitCode())
