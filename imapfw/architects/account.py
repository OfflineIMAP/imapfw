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

from .driver import DriverArchitect

from ..constants import ARC
from ..error import InterruptionError

from ..managers.account import AccountManager
from ..runners.account import SyncAccount
from ..runners.runner import ConsumerRunner


#TODO: rework
class AccountArchitectEventsInterface(object):
    def joinEndDrivers(self):   raise NotImplementedError
    def killEndDrivers(self):   raise NotImplementedError

class AccountArchitectInterface(AccountArchitectEventsInterface):
    def continueServing(self):  raise NotImplementedError
    def serve_nowait(self):     raise NotImplementedError
    def start(self):            raise NotImplementedError
    def kill(self):             raise NotImplementedError


#TODO: prefix internal method with _.
class AccountArchitect(AccountArchitectInterface):
    """Handling an account with 2 end-drivers.

    Build, serve and destroy the pipeline from end to end. Does not care what is
    done _within_ the pipeline. This is the role of the engine which is put in
    the "middle".

    Provides facilities for both the caller and the account manager."""

    def __init__(self):
        self.ui = runtime.ui

        self._leftArchitect = None
        self._rightArchitect = None
        self._accountEmitter = None
        self._accountReceiver = None
        self._syncAccount = None
        self._workerName = None
        self._accountTasks = None
        self._continueServing = False
        self._foldersArchitect = None

    def _getName(self):
        return self.__class__.__name__

    def continueServing(self):
        return self._continueServing

    def joinEndDrivers(self):
        self.ui.debugC(ARC, "%s joining end-drivers"% self._getName())
        self._leftArchitect.join()
        self._rightArchitect.join()

    def kill(self):
        self._continueServing = False
        self.killEndDrivers()
        self.ui.debugC(ARC, "%s killing account receiver"% self._getName())
        self._accountReceiver.kill()

    def killEndDrivers(self):
        self.ui.debugC(ARC, "%s killing end-drivers"% self._getName())
        self._leftArchitect.kill()
        self._rightArchitect.kill()

    def serve_nowait(self):
        """Serve the emitter."""

        try:
            self._continueServing = self._accountReceiver.serve_nowait()
            if self._continueServing is False:
                self.ui.debugC(ARC, "%s joining account receiver"% self._getName())
                #FIXME: join end-drivers if needed.
                self._accountReceiver.join()
        except InterruptionError:
            self.ui.debugC(ARC, "%s got InterruptionError"% self._getName())
            self.kill()

    def start(self, workerName, accountTasks, engineName):
        self.ui.debugC(ARC, "{} starting setup for '{}'", self._getName(),
            workerName)

        self._workerName = workerName
        self._accountTasks = accountTasks

        # Build and initialize the manager for this account worker.
        accountManager = AccountManager(self._workerName)

        # Get the emitter and receiver from the manager:
        # - the accountEmitter will run in the worker.
        # - the accountReceiver executes the orders of both the emitter and
        # the caller. It embedds the worker, too.
        self._accountEmitter, self._accountReceiver = accountManager.split()

        # Setup and start both end-drivers.
        self.ui.debugC(ARC, "{} starting end-drivers", self._getName())

        self._leftArchitect = DriverArchitect()
        self._rightArchitect = DriverArchitect()

        self._leftArchitect.start("%s.Driver.0"% self._workerName, self._accountEmitter)
        self._rightArchitect.start("%s.Driver.1"% self._workerName, self._accountEmitter)

        # Build the syncAccount runner which consumes the accountTasks. This is
        # the target of the worker. Notice the emitter of the account is passed
        # to this runner and the receiver is kept here: it's the engine (run
        # by the runner) which knows when to stop. Also, the receiver running in
        # the main worker, will be asked to start other workers.
        self._syncAccount = SyncAccount(
            self._accountTasks,
            self._accountEmitter, # The emitter for this account, yes.
            self._leftArchitect.getEmitter(),
            self._rightArchitect.getEmitter(),
            )

        self._continueServing = True
        self.ui.debugC(ARC, "{} starting account receiver", self._getName())
        self._accountReceiver.start(
            ConsumerRunner, # Top runner.
                (
                self._syncAccount,
                self.ui,
                self._workerName,
                self._accountTasks,
                self._accountEmitter,
                ),
            )
