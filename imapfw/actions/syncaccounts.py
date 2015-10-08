

from .interface import ActionInterface
from .helpers import setupConcurrency
from ..constants import WRK


class SyncAccounts(ActionInterface):
    """Sync the requested accounts as defined in the rascal, in async mode."""

    def __init__(self):
        self._exitCode = 0

        self._ui = None
        self._rascal = None
        self._concurrency = None
        self._accountList = None
        self._engineName = None

        self._accountsManager = None
        self._receivers = []

    def _getMaxSyncAccounts(self):
        return min(self._rascal.getMaxSyncAccounts(), len(self._accountList))

    def exception(self, e):
        self._exitCode = 7
        for receiver in self._receivers:
            receiver.kill()

    def getExitCode(self):
        return self._exitCode

    def initialize(self, ui, rascal, options):
        self._accountList = options.get('accounts')
        self._engineName = options.get('engine')

        self._ui, self._rascal, self._concurrency = setupConcurrency(
            ui, rascal)

    def run(self):
        """Enable the syncing of the accounts in an async fashion.

        Code here is about setting up the environment in order to start syncing
        at the very end.

        This method won't catch unexpected exceptions. This is of caller's
        responsability to handle them."""


        from ..concurrency.task import Task
        from ..managers.account import AccountManager
        from ..runners.runner import ConsumerRunner
        from ..runners.account import AccountTaskRunner

        # Sanity checks.
        if len(self._accountList) < 1:
            self._ui.error('no account given at command line')
            return

        # Turn the list of accounts into a queue for the workers.
        accountTasks = Task()
        for name in self._accountList:
            accountTasks.append(name)

        # Start the account workers to manage.
        for i in range(self._getMaxSyncAccounts()):
            workerName = "Account.Worker.%i"% i

            # Build and initialize the manager for this account worker.
            accountManager = AccountManager(
                self._ui,
                self._concurrency,
                workerName,
                self._rascal,
                )
            accountManager.initialize()

            # Get the emitter and receiver from the manager:
            # - the accountEmitter will run in the worker.
            # - the accountReceiver executes the orders of both the emitter and
            # the caller. It embedds the worker, too.
            accountEmitter, accountReceiver = accountManager.split()

            # Build the account runner from the generic task runner. This is the
            # target of the worker.
            # Notice the emitter of this account is run inside the worker!
            accountTaskRunner = AccountTaskRunner(
                self._ui,
                self._rascal,
                workerName,
                accountTasks,
                accountEmitter, # The emitter for this account, yes.
                accountReceiver.getLeftDriverEmitter(),
                accountReceiver.getRightDriverEmitter(),
                )

            # Start the account worker.
            accountReceiver.start(
                ConsumerRunner, # Runner.
                (accountTaskRunner, accountEmitter), # Arguments for the runner.
                )

            # We'll next have to serve this account emitter to execute the
            # orders. So, keep track of it.
            self._receivers.append(accountReceiver)

        # Serve the workers.
        self._ui.debug(WRK, "serving accounts")
        while len(self._receivers) > 0: # Are all account workers done?
            for accountReceiver in self._receivers:
                continueServing = accountReceiver.serve_nowait() # Async.
                if not continueServing:
                    accountReceiver.join() # Destroy the worker.
                    self._receivers.remove(accountReceiver)
        self._ui.debug(WRK, "serving accounts stopped")
