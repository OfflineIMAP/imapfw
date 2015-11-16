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

from imapfw.interface import Interface, implements, checkInterfaces

# Annotations.
from imapfw.annotation import DriverClass


class DriverInterface(Interface):
    """The Driver base class.

    This is the middleware for the drivers:
    - this is the base class to all drivers (e.g. Maildir, Driver, etc).
    - does not enable controllers machinery at this point.

    This interface is the API to anyone working with a driver (engines, shells,
    etc).
    """

    scope = Interface.INTERNAL

    conf = {} # The configuration of the type has to be there.
    isLocal = None

    def getClassName(self) -> str:
        """Return the class name, as defined by the rascal."""

    #TODO: why?
    def getDriverClassName(self) -> str:
        """Return the class name, as defined by the rascal."""

    def getRepositoryName(self) -> str:
        """Return the repository name of this driver."""

    def init(self) -> None:
        """Override this method to make initialization in the rascal."""

@checkInterfaces()
@implements(DriverInterface)
class Driver(object):
    def __init__(self, repositoryName: str, conf: dict):
        self.repositoryName = repositoryName
        self.conf = conf

    def getClassName(self) -> str:
        return self.__class__.__name__

    def getDriverClassName(self) -> str:
        return self.getClassName()

    def getRepositoryName(self) -> str:
        return self.repositoryName

    def init(self) -> None:
        pass


def loadDriver(cls_driver: DriverClass, repositoryName: str,
        repositoryConf: dict) -> Driver:

    # Build the final end-driver.
    if not issubclass(cls_driver, Driver):
        raise TypeError("driver %s of %s does not satisfy"
            " DriverInterface"% (cls_driver.__name__, repositoryName))

    driver = cls_driver(repositoryName, repositoryConf)
    driver.init()

    return driver
