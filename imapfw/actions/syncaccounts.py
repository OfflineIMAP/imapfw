# The MIT License (MIT).
# Copyright (c) 2015, Nicolas Sebrecht & contributors.

from imapfw import runtime
from imapfw.interface import implements, checkInterfaces
from imapfw.conf import Parser
from imapfw.architects.account import SyncAccountsArchitect

from .interface import ActionInterface

# Annotations.
from imapfw.annotation import ExceptionClass


@checkInterfaces()
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

    def init(self, parser: Parser) -> None:
        self.accountList = parser.get('accounts')
        self.engineName = parser.get('engine')

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


# syncAccounts CLI options.
actionParser = Parser.addAction('syncAccounts',
    SyncAccounts, help="sync on or more accounts")

actionParser.add_argument("-a", "--account", dest="accounts",
    default=[],
    action='append',
    metavar='ACCOUNT',
    required=True,
    help="one or more accounts to sync")

actionParser.add_argument("-e", "--engine", dest="engine",
    default="SyncAccount",
    help="the sync engine")
