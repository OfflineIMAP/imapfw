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

from typing import TypeVar


DriverClass = TypeVar('Driver based class')


class DriverInternalInterface(object):
    pass


class DriverInterface(object):

    conf = {} # The configuration of the type has to be there.
    isLocal = None

    def connect(self):              raise NotImplementedError
    def getClassName(self):         raise NotImplementedError
    def getFolders(self):           raise NotImplementedError
    def getRepositoryName(self):    raise NotImplementedError
    def logout(self):               raise NotImplementedError


class Driver(DriverInterface):
    """The Driver base class.

    The `fw_` namespace is reserved to the framework internals."""

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
        """Override this method to make initialization in the rascal."""

        pass


def loadDriver(cls_driver: DriverClass, repositoryName: str,
        repositoryConf: dict) -> Driver:

    # Build the final end-driver.
    if not issubclass(cls_driver, DriverInterface):
        raise TypeError("driver %s of %s does not satisfy"
            " DriverInterface"% (cls_driver.__name__, repositoryName))

    driver = cls_driver(repositoryName, repositoryConf)
    driver.init()

    return driver
