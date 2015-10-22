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

from ..mmp.account import AccountManager
from ..mmp.manager import receiverRunner


class AccountArchitectInterface(object):
    def getExitCode(self):  raise NotImplementedError
    def join(self):         raise NotImplementedError
    def kill(self):         raise NotImplementedError
    def setup(self):        raise NotImplementedError
    def start(self):        raise NotImplementedError


#TODO: SyncAccountArchitect from this.
class AccountArchitect(AccountArchitectInterface):
    """Handling an account with 2 end-drivers.

    Build, serve and destroy the pipeline from end to end. Does not care what is
    done _within_ the pipeline. This is the role of the engine which is put in
    the "middle".

    Provides facilities for both the caller and the account manager."""

    def __init__(self, engineName):
        self._engineName = engineName

        self.ui = runtime.ui
        self.concurrency = runtime.concurrency

        self._leftArchitect = None
        self._rightArchitect = None
        self._accountEmitter = None
        self._worker = None
        self._name = self.__class__.__name__
        self._exitCode = -1 # Let's the caller know that we are busy.

    def _kill(self):
        self.ui.debugC(ARC, "%s killing"% self._name)
        self._accountEmitter.stopServing()
        self._leftArchitect.kill()
        self._rightArchitect.kill()
        self._worker.kill()

    def _onNext(self, shouldRun):
        """Callback for when the account tried to get a new accountName."""

        if shouldRun is True:
            # The worker has an accountName to process.
            self._accountEmitter.run()
        else:
            # No more accountName, we are done! _stop
            self.ui.debugC(ARC, "%s stops"% self._name)
            self._exitCode = 0
            self._accountEmitter.stopServing()
            self._leftArchitect.stop()
            self._rightArchitect.stop()
            self._worker.join()

    def _onRunSuccess(self, syncFolders, maxFolderWorkers, accountName):
        #TODO: start folder workers, run sync, monitor.
        self._accountEmitter.getNextAccountName(self._engineName)

    def _onRunError(self, cls_Exception, reason):
        self._exitCode = 3 # See manual.
        self._kill()
        try:
            # We need to re-throw/catch the error so it can be passed to the
            # exception hook correctly.
            try:
                raise cls_Exception(reason)
            except Exception as e:
                raise Exception("could not cleany raise %s(%s): %s"%
                    cls_Exception, reason, e)
        except Exception as e:
            pass #TODO: honor hook!
            #exceptionHook(e)

    def getExitCode(self):
        """Caller must monitor the exit code to know when we are done.

        - negative: busy.
        - zero: finished without error.
        - positive: got unrecoverable error."""

        # Block until all results from previous requests are processed.
        # Finalizer callbacks triggered at this pass will update the exit code
        # when appropriate.
        try:
            self._accountEmitter.process_results()
        except Exception as e:
            self.ui.critical("account emitter for %s got unexpected error '%s'"%
                    (self._name, e))
            self._kill()
            raise
        return self._exitCode

    def start(self, workerName, accountTasks):
        """Setup and initiate one account worker. Not blocking."""

        self.ui.debugC(ARC, "{} starting setup for '{}'", self._name,
            workerName)

        # Setup and start both end-drivers.
        self.ui.debugC(ARC, "{} starting end-drivers", self._name)

        self._leftArchitect = DriverArchitect("%s.Driver.0"% workerName)
        self._rightArchitect = DriverArchitect("%s.Driver.1"% workerName)

        self._leftArchitect.start()
        self._rightArchitect.start()

        # Build and initialize the manager for this account worker.
        accountManager = AccountManager(workerName, accountTasks,
            self._leftArchitect.getEmitter('account'),
            self._rightArchitect.getEmitter('account'),
            )

        # The receiver is run in the worker and has full access to the manager.
        accountReceiver = accountManager.getReceiver()
        # The only available emitter is 'action' which provides:
        # - getNextAccountName()
        # - run()
        # - stopServing()
        self._accountEmitter = accountManager.getEmitter('action')

        # Callbacks define the flow of processing.
        self._accountEmitter.getNextAccountName.addOnSuccess(self._onNext)
        self._accountEmitter.run.addOnSuccess(self._onRunSuccess)
        self._accountEmitter.run.addOnError(self._onRunError)

        self._worker = self.concurrency.createWorker(
            workerName,
            receiverRunner,
            (accountReceiver,),
            )

        self.ui.debugC(ARC, "{} starting account receiver", self._name)
        self._worker.start()

        # Initiate the process in async mode: does not block!
        self._accountEmitter.getNextAccountName(self._engineName)
