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

import traceback

from imapfw import runtime

from .engine import Engine

from ..types.account import Account
from ..constants import WRK


class SyncFolder(Engine):
    """The engine to sync a folder in a worker."""

    def __init__(self, workerName, tasks, leftAgent, rightAgent,
        accountName, folderAgent):

        self._workerName = workerName
        self._tasks = tasks
        self._left = leftAgent
        self._rght = rightAgent
        self._accountName = accountName
        self._folderAgent = folderAgent

        self.ui = runtime.ui
        self.rascal = runtime.rascal

    def _consume(self, folder):
        pass

    def _infoL(self, level, msg):
        self.ui.infoL(level, "%s %s"% (self._workerName, msg))

    def run(self):
        try:
            account = self.rascal.get(self._accountName, [Account])
            leftRepository, rightRepository = self.getRepositories(
                account, self.rascal)

            self._left.buildDriver(leftRepository.getName(), _nowait=True)
            self._rght.buildDriver(rightRepository.getName(), _nowait=True)

            self._left.connect(_nowait=True)
            self._rght.connect(_nowait=True)

            while True:
                task =  self._tasks.get_nowait()
                if task is None: # No more task.
                    break # Quit the consumer loop.

                self._infoL(2, "syncing folder '%s'"% task)
                self._consume(task)
                self._infoL(3, "syncing folder '%s' done"% task)

            self._left.logout(_nowait=True)
            self._rght.logout(_nowait=True)
            self._left.stopServing(_nowait=True)
            self._rght.stopServing(_nowait=True)
            self._folderAgent.stopServing(_nowait=True)
            self.ui.debugC(WRK, "runner ended")
        except Exception as e:
            self.ui.error('%s exception occured: %s\n%s', self._workerName,
                e, traceback.format_exc())
            # In threading: will send logout() to drivers from
            # driverArchitect.kill().
            # In multiprocessing: will send SIGTERM.
            self._folderAgent.interruptionError(e.__class__, str(e))
