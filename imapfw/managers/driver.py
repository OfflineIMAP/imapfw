
from ..managers.manager import Manager
from ..drivers.driver import DriverBase
from ..types.repository import RepositoryInterface
from ..constants import DRV


class DriverManagerInterface(object):
    pass #TODO


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
        if self._driver.isLocal:
            self.ui.debugC(DRV, '{} working in {}', self._driver.getOwner(),
                self._driver.conf.get('path'))
        else:
            self.ui.debugC(DRV, '{} connecting to {}:{}', self._driver.getOwner(),
                self._driver.conf.get('host'), self._driver.conf.get('port'))

        #TODO: catch exception.
        connected = self._driver.connect()
        self.ui.debugC(DRV, "driver of {} connected", self._driver.getOwner())
        if not connected:
            raise Exception("%s: driver could not connect"% self.workerName)

    def exposed_fetchFolders_nowait(self):
        self.ui.debugC(DRV, "driver of {} starts fetching of folders",
            self._driver.getOwner())
        self._folders = self._driver.getFolders()

    def exposed_getFolders(self):
        self.ui.debugC(DRV, "driver of {} got folders: {}",
            self._driver.getOwner(), self._folders)
        return self._folders

    def exposed_logout(self):
        self._driver.logout()
        self.ui.debugC(DRV, "driver of {} logged out", self._driver.getOwner())

    def exposed_startDriver(self, typeName):
        # Retrieve the driver from the type.
        typeInst = self._rascal.get(typeName, [RepositoryInterface]) #TODO: defaultConstructor

        driver = typeInst.driver() # Instanciate the driver.
        driver.fw_initialize(self.ui, typeInst.conf, typeName) # Initialize.
        DriverBase.fw_sanityChecks(driver) # Catch common errors early.

        self.ui.debugC(DRV, "starting driver '{}' of '{}'",
            driver.getName(), driver.getOwner())
        self.ui.debugC(DRV, "'{}' has conf {}", driver.getOwner(), driver.conf)

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
