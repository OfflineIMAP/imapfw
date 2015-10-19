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

from ..managers.account import AccountManager
from ..engines.account import SyncAccount



class AccountArchitectInterface(object):
    def continueServing(self):  raise NotImplementedError
    def serve_next(self):       raise NotImplementedError
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
        self.concurrency = runtime.concurrency

        self._leftArchitect = None
        self._rightArchitect = None
        self._accountReceiver = None
        self._worker = None
        self._workerName = None

    def _getName(self):
        return self.__class__.__name__

    def join(self):
        self.ui.debugC(ARC, "%s joining"% self._getName())
        self._join()
        self._leftArchitect.join()
        self._rightArchitect.join()

    def kill(self):
        self.ui.debugC(ARC, "%s killing"% self._getName())
        self._worker.kill()
        self._leftArchitect.kill()
        self._rightArchitect.kill()

    def serve_next(self):
        return self._accountReceiver.serve_next()

    def start(self, workerName, accountTasks, engineName):
        self.ui.debugC(ARC, "{} starting setup for '{}'", self._getName(),
            workerName)

        self._workerName = workerName

        # Build and initialize the manager for this account worker.
        accountManager = AccountManager(self._workerName)

        # Get the emitter and receiver from the manager:
        # - the accountEmitter will run in the worker.
        # - the accountReceiver executes the orders of both the emitter and
        # the caller.
        self._accountReceiver, accountEmitter = accountManager.split()

        # Setup and start both end-drivers.
        self.ui.debugC(ARC, "{} starting end-drivers", self._getName())

        self._leftArchitect = DriverArchitect("%s.Driver.0"% self._workerName)
        self._rightArchitect = DriverArchitect("%s.Driver.1"% self._workerName)

        self._leftArchitect.start(accountEmitter)
        self._rightArchitect.start(accountEmitter)

        # Build the syncAccount engine which consumes the accountTasks. This is
        # the runner of the worker. Notice the emitter of the account is passed
        # to the engine and the receiver is kept here: it's of the engine
        # responsability to tell when to stop. Also, the receiver (running in
        # the main worker) will be asked to start other workers which is not
        # something possible from daemons.
        syncAccount = SyncAccount(
            workerName,
            accountTasks,
            accountEmitter, # The emitter for this account, yes.
            self._leftArchitect.getEmitter(),
            self._rightArchitect.getEmitter(),
            )

        self._worker = self.concurrency.createWorker(
            workerName,
            syncAccount.run,
            (),
            )

        self.ui.debugC(ARC, "{} starting account receiver", self._getName())
        self._worker.start()
