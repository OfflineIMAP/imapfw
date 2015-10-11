
from ..types.account import Account

class AccountTaskRunnerInterface(object):
    def getTask(self):
        raise NotImplementedError

    def getUIinst(self):
        raise NotImplementedError

    def getWorkerName(self):
        raise NotImplementedError

    def consume(self):
        raise NotImplementedError


class AccountTaskRunner(AccountTaskRunnerInterface):
    """The runner to consume an account.

    Designed to run inside the ConsummerRunner.

    Prepare the environement inside the worker and run the engine.
    """

    def __init__(self, ui, rascal, workerName, tasks, accountEmitter, left, right):
        self._ui = ui
        self._rascal = rascal
        self._workerName = workerName
        self._tasks = tasks
        self._accountEmitter = accountEmitter
        self._left = left # Control the left driver (emitter).
        self._right = right # Control the right driver (emitter).

        self._engine = None

    def getTask(self):
        return self._tasks.getTask()

    def getUIinst(self):
        return self._ui

    def getWorkerName(self):
        return self._workerName

    def consume(self, accountName):
        """The runner for syncing an account in a worker.

        :accountName: the account name to sync.
        """

        # The account class is defined in the rascal.
        account = self._rascal.get(accountName, [Account]) #TODO: defaultConstructor

        self._left.startDriver(account.left.__name__)
        self._right.startDriver(account.right.__name__)

        # Connect the drivers.
        self._left.connect_nowait()
        self._right.connect_nowait()

        # Use the engine for this account as defined in the rascal.
        engine = account.engine(
            self._ui,
            self._workerName,
            account,
            self._left,
            self._right,
            )
        engine.run()

        self._left.stopServing()
        self._right.stopServing()
