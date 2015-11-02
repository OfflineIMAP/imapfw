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
            accountName: str, engineName=None):
        super(FolderRunner, self).__init__(referent, left, right, engineName)

        self._accountName = accountName

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

        #
        # Loop over the available folder names.
        #
        for folder in Channel(folderQueue):
            self.processing(folder)

            # The engine will let explode errors it can't recover from.
            try:
                engine = SyncFolder(self.workerName,
                      self.left, self.right)
                import time
                import random
                sleep = random.randint(1, 3)
                self.debug('sleeping %i'% sleep)
                time.sleep(sleep)
                exitCode = engine.run()
                self.setExitCode(exitCode)

            except Exception as e:
                self.ui.exception(e)
                #TODO: honor hook!
                self.setExitCode(10) # See manual.

        self.checkExitCode()
        self.referent.stop(self.exitCode)
