
from collections import deque

from .driver import DriverArchitect

from ..constants import ARC
from ..error import InterruptionError

from ..managers.account import AccountManager
from ..runners.account import SyncAccount
from ..runners.runner import ConsumerRunner


class AccountArchitectEventsInterface(object):
    def honorEvents(self):      raise NotImplementedError
    def joinEndDrivers(self):   raise NotImplementedError
    def killEndDrivers(self):   raise NotImplementedError

class AccountArchitectInterface(AccountArchitectEventsInterface):
    def continueServing(self):  raise NotImplementedError
    def serve_nowait(self):     raise NotImplementedError
    def start(self):            raise NotImplementedError
    def kill(self):             raise NotImplementedError


class AccountArchitect(AccountArchitectInterface):
    """Handling an account with 2 end-drivers.

    Build, serve and destroy the pipeline from end to end. Does not care what is
    done _within_ the pipeline. This is the role of the engine which is put in
    the "middle".

    Provides facilities for both the caller and the account manager."""

    def __init__(self, ui, concurrency, rascal):
        self._ui = ui
        self._concurrency = concurrency
        self._rascal = rascal

        self._leftArchitect = None
        self._rightArchitect = None
        self._accountEmitter = None
        self._accountReceiver = None
        self._syncAccount = None
        self._workerName = None
        self._accountTasks = None
        self._continueServing = False
        self._events = deque() # Let the account receiver send us events.

    def continueServing(self):
        return self._continueServing

    def honorEvents(self):
        eventsMap = {
            }
        try:
            while True:
                event = self._events.popleft()

        except IndexError:
            pass

    def joinEndDrivers(self):
        self._leftArchitect.join()
        self._rightArchitect.join()

    def kill(self):
        self._continueServing = False
        self.killEndDrivers()
        self._accountReceiver.kill()

    def killEndDrivers(self):
        self._leftArchitect.kill()
        self._rightArchitect.kill()

    def serve_nowait(self):
        """Serve the emitter."""

        try:
            #TODO: use an event.
            self._continueServing = self._accountReceiver.serve_nowait()
            if self._continueServing is False:
                self._accountReceiver.join()
        except InterruptionError:
            self.kill()

    def start(self, workerName, accountTasks, engineName):
        self._ui.debugC(ARC, "starting setup for '{}'", workerName)

        self._workerName = workerName
        self._accountTasks = accountTasks

        # Build and initialize the manager for this account worker.
        accountManager = AccountManager(
            self._ui,
            self._concurrency,
            self._workerName,
            self._rascal,
            self._events,
            )
        # Get the emitter and receiver from the manager:
        # - the accountEmitter will run in the worker.
        # - the accountReceiver executes the orders of both the emitter and
        # the caller. It embedds the worker, too.
        self._accountEmitter, self._accountReceiver = accountManager.split()

        # Setup and start both end-drivers.
        self._leftArchitect = DriverArchitect(
            self._ui, self._concurrency, self._rascal)
        self._rightArchitect = DriverArchitect(
            self._ui, self._concurrency, self._rascal)
        self._leftArchitect.start("%s.Driver.0"% self._workerName, self._accountEmitter)
        self._rightArchitect.start("%s.Driver.1"% self._workerName, self._accountEmitter)

        # Build the syncAccount runner which consumes the accountTasks. This is
        # the target of the worker. Notice the emitter of the account is passed
        # to this runner and the receiver is kept here: it's the engine (run
        # by the runner) which knows when to stop. Also, the receiver running in
        # the main worker, will be asked to start other workers.
        self._syncAccount = SyncAccount(
            self._ui,
            self._rascal,
            self._accountTasks,
            self._accountEmitter, # The emitter for this account, yes.
            self._leftArchitect.getEmitter(),
            self._rightArchitect.getEmitter(),
            )

        self._continueServing = True
        self._accountReceiver.start(
            ConsumerRunner, # Top runner.
                (
                self._syncAccount,
                self._ui,
                self._workerName,
                self._accountTasks,
                self._accountEmitter,
                ),
            )
