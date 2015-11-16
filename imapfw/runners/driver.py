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

import inspect

from imapfw import runtime
from imapfw.constants import DRV
from imapfw.types.account import loadAccount
from imapfw.types.repository import Repository, loadRepository

# Annotations.
from imapfw.annotation import Dict, Union
from imapfw.edmp import Receiver
from imapfw.types.folder import Folders, Folder


#TODO: catch exceptions?
class DriverRunner(object):
    """The Driver to make use of any driver (with the controllers).

    Runs a complete low-level driver in a worker.

    The low-level drivers and controllers use the same low-level interface which
    is not directly exposed to the engine.

    Also, this allows to re-use any running worker with different repositories
    during its lifetime. This feature is a requirement of the SyncAccount
    runner.

    Some tasks require a referent for the following events:
        - exception(msg: str)
        - folders(lst_folders: Folders)
    """

    def __init__(self, workerName: str, receiver: Receiver):
        self.receiver = receiver

        self.repositoryName = 'UNKOWN_REPOSITORY'
        self.driver = None # Might change over time.

        # Cached values.
        self.folders = None
        self.capability = None

    def __getattr__(self, name):
        return getattr(self.driver, name)

    def _debug(self, msg):
        runtime.ui.debugC(DRV, "%s %s"% (self.repositoryName, msg))

    def buildDriverFromRepositoryName(self, repositoryName: str) -> None:
        """Build the driver object in the worker from this repository name.

        The repository must be globally defined in the rascal."""

        cls_repository = runtime.rascal.get(repositoryName, [Repository])
        repository = loadRepository(cls_repository)
        self.driver = repository.fw_getDriver()
        self.repositoryName = repositoryName
        runtime.ui.info("driver %s ready!"% self.driver.getClassName())

    def buildDriver(self, accountName: str, side: str,
            reuse: bool=False) -> None:
        """Build the driver object in the worker from this account side."""

        if reuse is True and self.driver is not None:
            return None

        self.driver = None

        # Build the driver.
        account = loadAccount(accountName)
        repository = account.fw_getSide(side)
        driver = repository.fw_getDriver()
        self.repositoryName = repository.getClassName()

        #TODO: move to a debug controller.
        runtime.ui.debugC(DRV, "built driver '{}' for '{}'",
                driver.getClassName(), driver.getRepositoryName())
        runtime.ui.debugC(DRV, "'{}' has conf {}", repository.getClassName(),
                driver.conf)

        self.driver = driver
        return driver

    def connect(self) -> bool:
        """Connect the driver for this repository (name)."""

        #TODO: move those debug logs into a controller.
        if self.driver.isLocal:
            self._debug("working in %s"% self.driver.conf.get('path'))
        else:
            self._debug("connecting to %s:%s"% (
                self.driver.conf.get('host'), self.driver.conf.get('port')))

        return self.driver.connect()

    def fetchCapability(self):
        self.capability = self.driver.capability()
        return self.capability

    def fetchFolders(self) -> Folders:
        """Fetch the folders and cache the result."""

        self._debug("starts fetching folder names")
        self.folders = self.driver.getFolders()
        return self.folders

    def getCapability(self):
        return self.capability

    def getFolders(self) -> Folders:
        """Return the cached folders."""

        self._debug("got folders: %s"% self.folders)
        return self.folders

    def login(self) -> None:
        return self.driver.login()

    def logout(self) -> None:
        """Logout from server.

        WARNING: this should NEVER be called in async mode since this can be
        racy.

        Can be called more than once."""

        if self.driver is not None:
            self.driver.logout()
            self._debug("logged out")
            self.driver = None
        return True

    def run(self) -> None:
        runtime.ui.debugC(DRV, "manager running")

        # Bind all public methods to events.
        for name, method in inspect.getmembers(self, inspect.ismethod):
            if name.startswith('_') or name == 'run':
                continue
            self.receiver.accept(name, method)

        while self.receiver.react():
            pass

    def select(self, mailbox: Union[Folder, str]) -> bool:
        """Select this mailbox."""

        return self.driver.select(str(mailbox))
