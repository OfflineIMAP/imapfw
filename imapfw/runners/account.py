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

from imapfw.constants import WRK
from imapfw.edmp import Channel

from imapfw.engines.account import SyncAccount
from imapfw.types.account import Account

# Annotations.
from imapfw.concurrency import Queue
from imapfw.edmp import Emitter



class AccountRunner(object):
    """The account runner.

    Setup the engine and run it. So, this does NOT defines what the worker
    actually does since it's the purpose of the engines.

    The code is run into the account worker.

    Will emit the following events to the referent:
        - syncFolders: called once Folders are merged.
        - runDone: called when no more task to process.
    """

    def __init__(self, referent: Emitter, left: Emitter, right: Emitter,
            engineName=None):

        self._referent = referent
        self._left = left
        self._rght = right
        self._engineName = engineName

        self.ui = runtime.ui

        self._workerName = None
        self._exitCode = -1 # Force the run to set a valid exit code.

    def _debug(self, msg: str):
        runtime.ui.debugC(WRK, "%s: %s"% (self._workerName, msg))

    def _setExitCode(self, exitCode):
        if exitCode > self._exitCode:
            self._exitCode = exitCode

    # Outlined.
    def _syncAccount(self, account, accountName):
        try:
            maxFolderWorkers, folders = self._engine.run(account)
            self._referent.syncFolders(accountName, maxFolderWorkers,
                    folders)

            # Wait until folders are synced.
            while self._referent.wait_sync():
                pass

        except Exception as e:
            self.ui.error("could not sync account %s"% accountName)
            self.ui.exception(e)
            self._setExitCode(10)

    def run(self, workerName: str, accountQueue: Queue):
        """The runner for the topRunner.

        Sequentially process the accounts, setup and run the engine."""

        self._workerName = workerName

        #
        # Loop over the available account names.
        #
        engine = None
        for accountName in Channel(accountQueue):
            self._debug("processing task: %s"% accountName)
            self._referent.running()

            # The engine will let expode errors it can't recover from.
            try:
                # Get the account instance from the rascal.
                account = runtime.rascal.get(accountName, [Account])

                if self._engineName is not None:
                    # Engine defined at CLI.
                    engineName = self._engineName
                else:
                    engineName = account.engine

                if engineName == 'SyncAccount':
                    engine = SyncAccount(self._workerName,
                            self._left, self._rght)
                    self._engine = engine
                    self._syncAccount(account, accountName)
                    self._setExitCode(0)

            except Exception as e:
                self.ui.exception(e)
                #TODO: honor hook!
                self._setExitCode(10) # See manual.

        #TODO: should we stop or wait until referent orders to?
        if self._exitCode < 0:
            if engine is None:
                self.ui.critical("%s had no account to sync"% self._workerName)
            else:
                self.ui.critical("%s exit code not set correctly"% self._workerName)
            self._setExitCode(99)
        self._referent.stop(self._exitCode)
