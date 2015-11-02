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

from .runner import TwoSidesRunner

# Annotations.
from imapfw.concurrency import Queue
from imapfw.edmp import Emitter



class AccountRunner(TwoSidesRunner):
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
        super(AccountRunner, self).__init__(referent, left, right, engineName)

    # Outlined.
    def _syncAccount(self, account, accountName):
        try:
            maxFolderWorkers, folders = self.engine.run(account)
            self.referent.syncFolders(accountName, maxFolderWorkers,
                folders)

            # Wait until folders are synced.
            while self.referent.wait_sync():
                pass

            self.setExitCode(0)

        except Exception as e:
            self.ui.error("could not sync account %s"% accountName)
            self.ui.exception(e)
            self.setExitCode(10)

    def run(self, workerName: str, accountQueue: Queue):
        """The runner for the topRunner.

        Sequentially process the accounts, setup and run the engine."""

        self.workerName = workerName

        #
        # Loop over the available account names.
        #
        engine = None
        for accountName in Channel(accountQueue):
            self.processing(accountName)
            self.referent.running()

            # The engine will let expode errors it can't recover from.
            try:
                # Get the account instance from the rascal.
                account = runtime.rascal.get(accountName, [Account])

                if self.engineName is not None:
                    # Engine defined at CLI.
                    engineName = self.engineName
                else:
                    engineName = account.engine

                if engineName == 'SyncAccount':
                    engine = SyncAccount(self.workerName,
                            self.left, self.right)
                    self.engine = engine
                    self._syncAccount(account, accountName)
                    self.setExitCode(0)

            except Exception as e:
                self.ui.exception(e)
                #TODO: honor hook!
                self.setExitCode(10) # See manual.

        self.checkExitCode()
        self.referent.stop(self.exitCode)
