# The MIT License (MIT).
# Copyright (c) 2015, Nicolas Sebrecht & contributors.

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

    # While updating this interface think about updating the fake controller,
    # too.

    scope = Interface.PUBLIC

    conf = {} # The configuration of the type has to be there.
    local = None

    def getClassName(self) -> str:
        """Return the class name, as defined by the rascal."""

    #TODO: why?
    def getDriverClassName(self) -> str:
        """Return the class name, as defined by the rascal."""

    def getRepositoryName(self) -> str:
        """Return the repository name of this driver."""

    def init(self) -> None:
        """Override this method to make initialization in the rascal."""

    def isLocal(self) -> bool:
        """Return True of False whether drived data is local."""


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

    def isLocal(self) -> bool:
        return self.local


def loadDriver(cls_driver: DriverClass, repositoryName: str,
        repositoryConf: dict) -> Driver:

    # Build the final end-driver.
    if not issubclass(cls_driver, Driver):
        raise TypeError("driver %s of %s does not satisfy"
            " DriverInterface"% (cls_driver.__name__, repositoryName))

    driver = cls_driver(repositoryName, repositoryConf)
    driver.init()

    return driver
