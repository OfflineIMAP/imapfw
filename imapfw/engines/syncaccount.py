
from ..constants import CTL


class SyncAccountEngineInterface(object):
    def run(self):
        raise NotImplementedError


class SyncAccount(SyncAccountEngineInterface):
    """Engine to sync an account.

    We have to compare the folder structures of both ends to know what folders
    to sync."""

    def __init__(self, ui, workerName, account, leftDriver, rightDriver):
        self._ui = ui
        self._workerName = workerName
        self._account = account # From the rascal.
        self._leftDriver = leftDriver
        self._rightDriver = rightDriver

    def run(self):
        """Compare the folders on both ends. Return a list of merged folders."""

        accountName = self._account.getName()

        # Get types from rascal.
        rascalLeft = self._account.left()
        rascalRight = self._account.right()

        # Fetch folders concurrently.
        rascalLeft.fetchFolders(self._leftDriver)
        rascalRight.fetchFolders(self._rightDriver)

        # Get the folders from both sides so we can feed the folder tasks.
        leftFolders = rascalLeft.getFolders(self._leftDriver)
        rightFolders = rascalRight.getFolders(self._rightDriver)

        # Merge the folder lists.
        mergedFolders = []
        for sideFolders in [leftFolders, rightFolders]:
            for folder in sideFolders:
                if folder not in mergedFolders:
                    mergedFolders.append(folder)

        # Pass the list to the account.
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
            self._ui.warn("rascal, you asked to sync non-existing folders"
                " for '%s': %s", accountName, ignoredFolders)

        if len(syncFolders) < 1:
            self._leftDriver.logout()
            self._rightDriver.logout()
            return

        ## Feed the folder tasks.
        #self._accountEmitter.startFolderWorkers(accountName, syncFolders)
        ## Block until all the folders are synced.
        #self._accountEmitter.serveFolderWorkers()

        #TODO: move out.
        # Leave the driver in Authenticated state.
        self._leftDriver.logout()
        self._rightDriver.logout()
