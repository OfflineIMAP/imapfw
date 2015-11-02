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

from imapfw.edmp import Channel

from imapfw.engines.folder import SyncFolder

from .runner import TwoSidesRunner

# Annotations.
from imapfw.edmp import Emitter
from imapfw.concurrency import Queue


class FolderRunner(TwoSidesRunner):
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
        super(FolderRunner, self).__init__(referent, left, right, engineName)

    # Outlined.
    def _syncFolder(self, folder: 'TODO'):
        try:
            pass
            # maxFolderWorkers, folders = self._engine.run(account)
            # self._referent.syncFolders(accountName, maxFolderWorkers,
                    # folders)

            # # Wait until folders are synced.
            # while self._referent.wait_sync():
                # pass

        except Exception as e:
            self.ui.error("could not sync folder %s"% folder)
            self.ui.exception(e)
            self.setExitCode(10)

    def run(self, workerName: str, folderQueue: Queue):
        """The runner for the topRunner.

        Sequentially process the folders, setup and run the engine."""

        self.workerName = workerName
        import time
        import random
        sleep = random.randint(7, 25)
        self.debug('sleeping %i'% sleep)
        time.sleep(sleep)

        # #
        # # Loop over the available account names.
        # #
        # engine = None
        # for folder in Channel(folderQueue):
            # self.debug("processing task: %s"% accountName)
            # self.referent.running()

            # # The engine will let expode errors it can't recover from.
            # try:
                # # Get the account instance from the rascal.
                # account = runtime.rascal.get(accountName, [Account])

                # if self._engineName is not None:
                    # # Engine defined at CLI.
                    # engineName = self._engineName
                # else:
                    # engineName = account.engine

                # if engineName == 'SyncAccount':
                    # engine = SyncAccount(self._workerName,
                            # self._left, self._rght)
                    # self._engine = engine
                    # self._syncAccount(account, accountName)

            # except Exception as e:
                # self.ui.exception(e)
                # #TODO: honor hook!
                # self._setExitCode(10) # See manual.

        # #TODO: should we stop or wait until referent orders to?
        # if self._exitCode < 0:
            # if engine is None:
                # self.ui.critical("%s had no account to sync"% self._workerName)
            # else:
                # self.ui.critical("%s exit code not set correctly"% self._workerName)
            # self._setExitCode(99)
        self.setExitCode(0) #TODO
        self.referent.stop(self.exitCode)
