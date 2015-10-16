

from .interface import ActionInterface

from ..constants import WRK
from ..architects.account import AccountArchitect


class SyncAccounts(ActionInterface):
    """Sync the requested accounts as defined in the rascal, in async mode."""

    honorHooks = True
    requireRascal = True

    def __init__(self):
        self._exitCode = 0

        self._ui = None
        self._rascal = None
        self._concurrency = None
        self._accountList = None
        self._engineName = None

        self._accountsManager = None
        self._receivers = []

    def _concurrentAccountsNumber(self):
        return min(self._rascal.getMaxSyncAccounts(), len(self._accountList))

    def exception(self, e):
        self._exitCode = 3
        for receiver in self._receivers:
            receiver.kill()

    def getExitCode(self):
        return self._exitCode

    def init(self, ui, concurrency, rascal, options):
        self._ui = ui
        self._concurrency = concurrency
        self._rascal = rascal

        self._accountList = options.get('accounts')
        self._engineName = options.get('engine')

    def run(self):
        """Enable the syncing of the accounts in an async fashion.

        Code here is about setting up the environment in order to start syncing
        at the very end.

        This method won't catch unexpected exceptions. This is of caller's
        responsability to handle them."""


        from ..concurrency.task import Tasks

        # Turn the list of accounts into a queue of tasks.
        accountTasks = Tasks()
        for name in self._accountList:
            accountTasks.append(name)

        # Setup the architecture.
        accountArchitects = []
        for i in range(self._concurrentAccountsNumber()):
            workerName = "Account.Worker.%i"% i

            accountName = self._accountList.pop(0)

            accountArchitect = AccountArchitect(self._ui, self._concurrency, self._rascal)
            accountArchitect.start(
                workerName, accountTasks, self._engineName)
            accountArchitects.append(accountArchitect)


        # Serve all the account workers.
        self._ui.debugC(WRK, "serving accounts")
        while len(accountArchitects) > 0: # Are all account workers done?
            try:
                for accountArchitect in accountArchitects:
                    accountArchitect.serve_nowait() # Does not block if nothing to do.
                    if accountArchitect.continueServing() is False:
                        accountArchitects.remove(accountArchitect)
            except:
                for accountArchitect in accountArchitects:
                    accountArchitect.kill()
                raise
        self._ui.debugC(WRK, "serving accounts stopped")
