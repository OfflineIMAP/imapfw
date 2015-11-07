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

from typing import TypeVar, Union

from imapfw.controllers.controller import loadController
from imapfw.drivers.driver import loadDriver


RepositoryClass = TypeVar('Repository based class')


class RepositoryInterface(object):

    conf = None
    driver = None
    isLocal = None

    def getClassName(self):      raise NotImplementedError
    def init(self):              raise NotImplementedError


class RepositoryIntenalInterface(object):
    def fw_addController(self):     raise NotImplementedError
    def fw_getDriver(self):         raise NotImplementedError
    def fw_insertController(self):  raise NotImplementedError


class Repository(RepositoryInterface, RepositoryIntenalInterface):
    """The repository base class.

    The `fw_` namespace is reserved to the framework internals. Any method of
    this namespace must be overriden."""

    conf = None
    driver = None
    controllers = []

    def __init__(self):
        # Turn the class attributes into instance attributes.
        self.conf = self.conf.copy()
        self.driver = self.driver
        self.controllers = self.controllers.copy()

    def fw_addController(self, controller):
        self.controllers.insert(0, controller)

    def fw_getDriver(self):
        """Chain the controllers on top of the driver.

        Controllers are run in the driver worker."""

        driver = loadDriver(self.driver, self.getClassName(), self.conf)

        # Chain the controllers.
        controllers = self.controllers # Keep the original attribute as-is.
        # Nearest to end-driver is the last in this list.
        controllers.reverse()
        for obj in controllers:
            controller = loadController(obj, self.getClassName(), self.conf)

            controller.fw_drive(driver) # Chain here.
            driver = controller # The next controller will drive this.

        return driver

    def fw_insertController(self, controller):
        self.controllers.insert(0, controller)

    def getClassName(self):
        return self.__class__.__name__

    def init(self):
        """Override this method to make initialization in the rascal."""

        pass


def loadRepository(obj: Union[RepositoryClass, dict]) -> Repository:

    try:
        if issubclass(obj, RepositoryInterface):
            cls_repository = obj
        else:
            raise TypeError()

    except TypeError:
        try:
            if not issubclass(obj, dict):
                raise TypeError()

            # The repository is defined in the dictionnary form in the rascal.
            # Build the class.
            cls_repository = type(obj.get('name'), obj.get('type'), {})

            # Attached attributes.
            for name, mandatory in {
                    'conf': True,
                    'driver': True,
                    'controllers': [],
                    }:
                try:
                    setattr(cls_repository, name, obj.get(name))
                except KeyError:
                    if mandatory is True:
                        raise Exception("mandatory key '%s' is not defined for"
                            " %s"% (name, cls_repository.__name__))
                    setattr(cls_repository, name, mandatory)

        except TypeError:
            raise TypeError("'%s' for a repository is not supported"% type(obj))

    repository = cls_repository()
    repository.init()

    return repository
