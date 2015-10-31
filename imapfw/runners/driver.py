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
from imapfw.types.repository import RepositoryInterface

# Annotations.
from imapfw.edmp import Receiver
from imapfw.types.folder import Folders


#TODO: catch exceptions?
class DriverRunner(object):
    """The Driver to make use of any driver with controllers.

    This object builds and runs a low-level driver (from rascal api.drivers) so
    it can be used in a worker.

    The low-level drivers and controllers use the same low-level interface which
    is not directly exposed to the engine.

    Also, this allow to re-use any running worker with different repositories
    during its lifetime.

    Some tasks require a referent for the following events:
        - exception(msg: str)
        - folders(lst_folders: Folders)
    """

    def __init__(self, receiver: Receiver):
        self._receiver = receiver

        self.ui = runtime.ui

        self._workerName = None
        self._driver = None # Might change over time.
        self._serve = True

        # Cached values.
        self._folders = None
        self._ownerName = None

    def _debug(self, msg):
        self.ui.debugC(DRV, "%s %s"% (self._ownerName, msg))

    def buildDriver(self, repositoryName: str):
        self._ownerName = repositoryName
        self._driver = None

        repository = runtime.rascal.get(repositoryName, [RepositoryInterface])
        repository.fw_init()

        # Build the driver.
        driver = repository.fw_chainControllers()
        driver.fw_init(repository.conf, repositoryName) # Initialize.
        driver.fw_sanityChecks(driver) # Catch common errors early.

        self.ui.debugC(DRV, "built driver '{}' for '{}'",
                driver.getName(), repositoryName)
        self.ui.debugC(DRV, "'{}' has conf {}", repositoryName, driver.conf)

        self._driver = driver

    def connect(self):
        """Connect the driver for this repository (name)."""

        if self._driver.isLocal:
            self._debug("working in %s"% self._driver.conf.get('path'))
        else:
            self._debug("connecting to %s:%s"% (
                self._driver.conf.get('host'), self._driver.conf.get('port')))

        return self._driver.connect()

    def fetchFolders(self):
        self._debug("starts fetching folder names")
        self._folders = self._driver.getFolders()
        return self._folders

    def getFolders(self) -> Folders:
        self._debug("got folders: %s"% self._folders)
        return self._folders

    def logout(self):
        self._driver.logout()
        self._debug("logged out")
        self._driver = None

    def run(self, workerName: str):
        self._workerName = workerName

        self.ui.debugC(DRV, "%s manager running"% workerName)

        # Bind all public methods to events.
        for name, method in inspect.getmembers(self):
            if name.startswith('_'):
                continue
            self._receiver.accept(name, method)

        while self._receiver.react():
            pass
