
from ..constants import DRV


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
        self._account = account
        self._leftDriver = leftDriver
        self._rightDriver = rightDriver

    def run(self):
        """Compare the folders on both ends. Return a list of merged folders."""

        folders = []
        accountName = self._account.getName()

        # Get the folders from both sides so we can feed the folder tasks.
        self._leftDriver.fetchFolders_nowait()
        self._rightDriver.fetchFolders_nowait()

        leftFolders = self._leftDriver.getFolders()
        rightFolders = self._rightDriver.getFolders()

        self._ui.debugC(DRV, "got left folders: %s"% leftFolders)
        self._ui.debugC(DRV, "got right folders: %s"% rightFolders)

        #TODO: move out.
        # Leave the driver in Authenticated state.
        self._leftDriver.logout()
        self._rightDriver.logout()

        #TODO: honor controllers


        ## Merge the folder lists.
        #for folder in leftFolders:
            #if folder not in folders:
                #folder.append(folder)

        ## Pass the list to the rascal.
        #rascalFolders = self._cls_account.syncFolders(folders)

        ## The rascal might request for non-existing folders!
        #syncFolders = []
        #ignoredFolders = []
        #for folder in rascalFolders:
            #if folder in folders:
                #syncFolders.append(folder)
            #else:
                #ignoredFolders.append(folder)
        #if len(ignoredFolders) > 0:
            #self._ui.warn("rascal, you asked to sync non-existing folders for '%s' %s",
                #accountName, ignoredFolders)

        ## Feed the folder tasks.
        #self._accountEmitter.startFolderWorkers(accountName, syncFolders)
        ## Block until all the folders are synced.
        #self._accountEmitter.serveFolderWorkers()
