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
from imapfw.architects.account import SyncAccountsArchitect

from .interface import ActionInterface


class SyncAccounts(ActionInterface):
    """Sync the requested accounts as defined in the rascal, in async mode."""

    honorHooks = True
    requireRascal = True

    def __init__(self):
        self.accountList = None
        self.engineName = None
        self.exitCode = -1

    def exception(self, e):
        # This should not happen since all exceptions are handled at lower level.
        raise NotImplementedError

    def getExitCode(self):
        return self.exitCode

    def init(self, options):
        self.accountList = options.get('accounts')
        self.engineName = options.get('engine')

    def run(self):
        """Enable the syncing of the accounts in an async fashion.

        Code here is about setting up the environment, start the jobs and
        monitor."""


        maxConcurrentAccounts = min(
            runtime.rascal.getMaxSyncAccounts(),
            len(self.accountList))

        accountsArchitect = SyncAccountsArchitect(self.accountList)
        accountsArchitect.start(maxConcurrentAccounts)
        self.exitCode = accountsArchitect.run()
