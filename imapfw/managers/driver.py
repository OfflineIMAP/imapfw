
from ..managers.manager import Manager
from ..drivers.driver import DriverInterface
from ..types.repository import RepositoryInterface
from ..constants import DRV


class DriverManagerInterface(object):
    pass # TODO


class DriverManager(Manager, DriverManagerInterface):
    """The driver manager.

    The receiver builds and runs the low-level driver (from rascal api.drivers).

    All the api.drivers types use the same DriverInterface interface. This
    interface is low-level interface which is not directly mapped as the public
    DriverManager interface.

    The user of the emitter controls both the worker and the driver. The user of
    the emitter change over time."""

    def __init__(self, ui, concurrency, workerName, rascal):
        super(DriverManager, self).__init__(ui, concurrency, workerName)

        self._rascal = rascal

        self._driver = None
        self._folders = None

        ui.debugC(DRV, "%s manager created"% workerName)

    def exposed_connect_nowait(self):
        connected = self._driver.connect()
        self.ui.debugC(DRV, "driver connected")
        if not connected:
            raise Exception("%s: could not connect the driver"% self.workerName)

    def exposed_fetchFolders_nowait(self):
        self.ui.debugC(DRV, "starting fetch of folders")
        self._folders = self._driver.getFolders()

    def exposed_getFolders(self):
        self.ui.debugC(DRV, "folders: {}", self._folders)
        return self._folders

    def exposed_logout(self):
        self._driver.logout()

    def exposed_startDriver(self, typeName):
        # Retrieve the driver from the type.
        typeInst = self._rascal.get(typeName, [RepositoryInterface]) #TODO: defaultConstructor

        driver = typeInst.driver() # Instanciate the driver.
        driver.fw_initialize(self.ui, typeInst.conf) # Initialize.
        driver.fw_sanityChecks() # Catch common errors early.

        self.ui.debugC(DRV, "starting driver '{}' of '{}'",
            driver.fw_getName(), typeName)
        self.ui.debugC(DRV, "'{}' has conf {}", typeName, driver.conf)

        self._driver = driver


def createSideDriverManager(ui, concurrency, rascal, HandlerName, number):
    """Enable the driver machinery for one side.

    Helper when two drivers are required, one for each side, each running
    concurrently."""

    driverName = "%s.Driver.%s"% (HandlerName, number)

    # Build the driver.
    drivermanager = DriverManager(
        ui,
        concurrency,
        driverName,
        rascal,
        )
    emitter, receiver = drivermanager.split()
    return emitter, receiver
