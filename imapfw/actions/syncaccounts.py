# The MIT License (MIT).
# Copyright (c) 2015, Nicolas Sebrecht & contributors.

from imapfw import runtime
from imapfw.architects.account import SyncAccountsArchitect
from imapfw.interface import implements

from .interface import ActionInterface

# Annotations.
from imapfw.annotation import ExceptionClass, Dict


@implements(ActionInterface)
class SyncAccounts(object):
    """Sync the requested accounts as defined in the rascal, in async mode."""

    honorHooks = True
    requireRascal = True

    def __init__(self):
        self.accountList = None
        self.engineName = None
        self.exitCode = -1

    def exception(self, e: ExceptionClass) -> None:
        self.exitCode = 3
        raise NotImplementedError #TODO

    def getExitCode(self) -> int:
        return self.exitCode

    def init(self, options: Dict) -> None:
        self.accountList = options.get('accounts')
        self.engineName = options.get('engine')

    def run(self) -> None:
        """Enable the syncing of the accounts in an async fashion.

        Code here is about setting up the environment, start the jobs and
        monitor."""


        maxConcurrentAccounts = min(
            runtime.rascal.getMaxSyncAccounts(),
            len(self.accountList))

        accountsArchitect = SyncAccountsArchitect(self.accountList)
        accountsArchitect.start(maxConcurrentAccounts)
        self.exitCode = accountsArchitect.run()
