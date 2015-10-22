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


from .manager import Manager

from ..engines.account import SyncAccount
from ..constants import MGR


class AccountManager(Manager):
    """The account manager to implement the receiver and define the emitter API.

    This does NOT defines what the worker actually does since this is the purpose
    of the engines.

    The only available emitter API is 'action'.

    The code of this object is run by the receiver into the account worker.
    All the returned values are sent from the receiver to the emitter."""


    def __init__(self, workerName, accountTasks, leftEmitter, rightEmitter):
        super(AccountManager, self).__init__()

        self._workerName = workerName
        self._accountTasks = accountTasks
        self._leftEmitter = leftEmitter
        self._rightEmitter = rightEmitter

        self._engine = None

    def _debug(self, msg):
        self.ui.debugC(MGR, "%s: %s"% (self._name, msg))

    def ex_action_getNextAccountName(self, engineName):
        self._accountName = self._accountTasks.get_nowait()

        if self._accountName is None:
            return False # Flag that there is no more task.

        # Build the engine.
        if engineName is 'SyncAccount':
            # Build the syncAccount engine which consumes the accountTasks.
            self._engine = SyncAccount(
                self._workerName,
                self._leftEmitter,
                self._rightEmitter,
                )

        return True # Receiver is ready for a run.

    def ex_action_run(self):
        self.ui.debug('would run the engine')
        return None, None, None
        self._engine.run(self._accountName)
        return self._engine.getResults()

    def ex_action_stopServing(self):
        self.stopServing()
