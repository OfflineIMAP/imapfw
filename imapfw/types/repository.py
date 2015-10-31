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

from ..constants import DRV


class RepositoryIntenalInterface(object):
    def fw_init(self):              raise NotImplementedError
    def fw_addController(self):     raise NotImplementedError
    def fw_chainControllers(self):  raise NotImplementedError


class RepositoryInterface(RepositoryIntenalInterface):

    conf = None
    driver = None
    isLocal = None

    def fetchFolders(self): raise NotImplementedError
    def getName(self):      raise NotImplementedError
    def getFolders(self):   raise NotImplementedError


class RepositoryBase(RepositoryInterface):

    conf = None
    driver = None

    def fw_init(self):
        self.ui = runtime.ui

        if not hasattr(self, 'controllers'):
            controllers = self.conf.get('controllers')
            if controllers is None:
                controllers = []
            self.controllers = controllers

    def fw_addController(self, controller):
        self.controllers.insert(0, controller)

    def fw_chainControllers(self):
        """Chain the controllers on top of the driver.

        Controllers are run in the driver worker, so return the result."""

        controllers = self.controllers # Avoid changing this attribute.
        driver = self.driver() # Instanciate end-driver.
        controllers.reverse() # Nearest from driver is the last in this list.
        for cls_controller in controllers:
            self.ui.debugC(DRV, "chaining driver '%s' with controller '%s'"%
                (driver.__class__.__name__, cls_controller.__name__))

            controller = cls_controller()
            controller.fw_drive(driver) # Chains here.
            driver = controller # The next controller will drive this.

        return driver

    def fetchFolders(self):
        return self.driver.fetchFolders()

    def getFolders(self):
        return self.driver.getFolders()

    def getName(self):
        return self.__class__.__name__
