# The MIT License (MIT).
# Copyright (c) 2015-2016, Nicolas Sebrecht & contributors.

import inspect

from imapfw import runtime
from imapfw.constants import DRV
from imapfw.types.account import loadAccount
from imapfw.types.repository import Repository, loadRepository

# Annotations.
from imapfw.edmp import Receiver


#TODO: catch exceptions?
class DriverRunner(object):
    """The Driver to make use of any driver (with the controllers).

    Runs a complete low-level driver in a worker.

    The low-level drivers and controllers use the same low-level interface which
    is directly exposed to the engine.

    Also, this runner allows to re-use any running worker with different
    repositories during its lifetime. This feature is a required by design.
    """

    #FIXME: unused workerName
    def __init__(self, workerName: str, receiver: Receiver):
        self.receiver = receiver

        self.repositoryName = None
        self.driver = None # Might change over time.
        self.repositoryName = 'UNKOWN_REPOSITORY'
        self.driver = None

    def _debug(self, msg: str) -> None:
        runtime.ui.debugC(DRV, "%s %s"% (self.repositoryName, msg))

    def _debugBuild(self):
        runtime.ui.debugC(DRV, "built driver '{}' for '{}'",
            self.driver.getClassName(), self.driver.getRepositoryName())
        runtime.ui.debugC(DRV, "'{}' has conf {}",
            self.repositoryName, self.driver.conf)

    def _driverAccept(self) -> None:
        for name, method in inspect.getmembers(self.driver, inspect.ismethod):
            if name.startswith('_') or name.startswith('fw_'):
                continue

            #FIXME: we should clear previous accepted events.
            self.receiver.accept(name, method)

    def _info(self, msg: str) -> None:
        runtime.ui.info("%s %s"% (self.repositoryName, msg))

    def _buildDriver(self, repository: Repository) -> None:
        self.repositoryName = repository.getClassName()
        self.driver = repository.fw_getDriver()
        self._driverAccept()
        self._debugBuild()
        self._info("driver ready!")

    def buildDriver(self, accountName: str, side: str,
            reuse: bool=False) -> None:
        """Build the driver object in the worker from this account side."""

        if reuse is True and self.driver is not None:
            return None

        account = loadAccount(accountName)
        repository = account.fw_getSide(side)
        self._buildDriver(repository)

    def buildDriverFromRepositoryName(self, repositoryName: str,
            reuse: bool=False) -> None:
        """Build the driver object in the worker from this repository name.

        The repository must be globally defined in the rascal."""

        if reuse is True and self.driver is not None:
            return None

        cls_repository = runtime.rascal.get(repositoryName, [Repository])
        repository = loadRepository(cls_repository)
        self._buildDriver(repository)

    def isDriverBuilt(self) -> bool:
        return self.driver is not None

    def logout(self) -> None:
        """Logout from server. Allows to be called more than once."""

        if self.driver is not None:
            self.driver.logout_sync()
            self._debug("logged out")
            self.driver = None
        return True

    def run(self) -> None:
        runtime.ui.debugC(DRV, "manager running")

        # Bind all public methods to events.
        for name in ['buildDriver', 'buildDriverFromRepositoryName',
                'isDriverBuilt', 'logout']:
            self.receiver.accept(name, getattr(self, name))

        while self.receiver.react():
            pass
