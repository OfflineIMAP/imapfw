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
from typing import Union

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
        self._workerName = workerName
        self._receiver = receiver

        self.ui = runtime.ui

        self._workerName = None
        self._driver = None # Might change over time.
        self._serve = True

        # Cached values.
        self._folders = None
        self._ownerName = None

    def __getattr__(self, name):
        return getattr(self._driver, name)

    def _debug(self, msg):
        self.ui.debugC(DRV, "%s %s"% (self._ownerName, msg))

    def buildDriverFromRepositoryName(self, repositoryName: str) -> None:
        cls_repository = runtime.rascal.get(repositoryName, [Repository])
        repository = loadRepository(cls_repository)
        self._driver = repository.fw_getDriver()
        runtime.ui.info("driver %s ready!"% self._driver.getClassName())

    def buildDriver(self, accountName: str, side: str,
            reuse: bool=False) -> None:
        if reuse is True and self._driver is not None:
            return None

        self._driver = None

        # Build the driver.
        account = loadAccount(accountName)
        repository = account.fw_getSide(side)
        driver = repository.fw_getDriver()

        #TODO: move to a debug controller.
        self.ui.debugC(DRV, "built driver '{}' for '{}'",
                driver.getClassName(), driver.getRepositoryName())
        self.ui.debugC(DRV, "'{}' has conf {}", repository.getClassName(),
                driver.conf)

        self._driver = driver
        return driver

    def connect(self) -> bool:
        """Connect the driver for this repository (name)."""

        #TODO: move those debug logs into a controller.
        if self._driver.isLocal:
            self._debug("working in %s"% self._driver.conf.get('path'))
        else:
            self._debug("connecting to %s:%s"% (
                self._driver.conf.get('host'), self._driver.conf.get('port')))

        return self._driver.connect()

    def fetchFolders(self) -> Folders:
        self._debug("starts fetching folder names")
        self._folders = self._driver.getFolders()
        return self._folders

    def getFolders(self) -> Folders:
        self._debug("got folders: %s"% self._folders)
        return self._folders

    def logout(self) -> None:
        if self._driver is not None:
            self._driver.logout()
            self._debug("logged out")
            self._driver = None
        return True

    def run(self) -> None:
        self.ui.debugC(DRV, "%s manager running"% self._workerName)

        # Bind all public methods to events.
        for name, method in inspect.getmembers(self, inspect.ismethod):
            if name.startswith('_') or name == 'run':
                continue
            self._receiver.accept(name, method)

        while self._receiver.react():
            pass

    def select(self, mailbox: Union[Folder, str]) -> bool:
        return self._driver.select(str(mailbox))
