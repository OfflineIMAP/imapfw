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

from .manager import Manager

from ..constants import DRV
from ..types.repository import RepositoryInterface


#TODO: catch exceptions?
class DriverManager(Manager):
    """The driver manager.

    The receiver builds and runs the low-level driver (from rascal api.drivers).

    All the api.drivers types use the same DriverInterface interface. This
    interface is low-level interface which is not directly mapped as the public
    DriverManager interface.

    The user of the emitter controls both the worker and the driver. The user of
    the emitter might over time.

    All the code here runs inside the worker."""

    def __init__(self, workerName):
        super(DriverManager, self).__init__()

        self._workerName = workerName

        self.ui = runtime.ui
        self.rascal = runtime.rascal

        self._driver = None # Might change over time.
        self._folders = None

        self.ui.debugC(DRV, "%s manager created"% workerName)

    def connect(self, repositoryName):
        """Connect the driver for this repository (name)."""

        repository = self.rascal.get(repositoryName, [RepositoryInterface])
        repository.fw_init()

        # Build the driver.
        driver = repository.fw_chainControllers()
        driver.fw_init(repository.conf, repositoryName) # Initialize.
        driver.fw_sanityChecks(driver) # Catch common errors early.

        self.ui.debugC(DRV, "built driver '{}' for '{}'",
            driver.getName(), repositoryName)
        self.ui.debugC(DRV, "'{}' has conf {}", repositoryName, driver.conf)

        # Ready, connect.
        if driver.isLocal:
            self.ui.debugC(DRV, '{} working in {}', driver.getOwnerName(),
                driver.conf.get('path'))
        else:
            self.ui.debugC(DRV, '{} connecting to {}:{}',
                driver.getOwnerName(), driver.conf.get('host'),
                driver.conf.get('port'))

        connected = driver.connect()
        self.ui.debugC(DRV, "driver of {} connected", driver.getOwnerName())
        if connected:
            self._driver = driver
        else:
            raise Exception("%s: driver could not connect"% self._workerName)

    def ex_account_connect(self):
        self.connect()

    def ex_account_fetchFolders(self):
        self.ui.debugC(DRV, "driver of {} starts fetching of folders",
            self._driver.getOwnerName())
        self._folders = self._driver.getFolders()

    def ex_account_getFolders(self):
        self.ui.debugC(DRV, "driver of {} got folders: {}",
            self._driver.getOwnerName(), self._folders)
        return self._folders

    def ex_account_logout(self):
        self._driver.logout()
        self.ui.debugC(DRV, "driver of {} logged out", self._driver.getOwnerName())
        self._driver = None

    def ex_architect_stopServing(self):
        self.stopServing()
