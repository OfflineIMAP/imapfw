
from ..managers.manager import Manager
from ..drivers.driver import DriverInterface
from ..constants import DRV


#class DriverWorkerManager(Manager):

    ## DriverWorkerManager
    #def start(self):
        #"""Receiver API."""

        #self.worker = self.concurrency.createWorker(
            #name=self.managerName,
            #target=driverRunner,
            #args=(
                #self.managerName,
                #self.get_proxy(),
            #)
        #)
        #self.worker.start()
        #self.ui.debug(WRK, "%s started"% self.managerName)
        #driverManager = DriverManager(name, )

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

    driverExpose = [
        'connect_nowait',
        'fetchFolders_nowait',
        'getFolders',
        'startDriver',
        ]

    def __init__(self, ui, concurrency, workerName, rascal):
        super(DriverManager, self).__init__(ui, concurrency, workerName)

        self._rascal = rascal

        self._cls_driver = None
        self._driver = None
        self._folders = None

        self.expose(self.driverExpose)

        ui.debug(DRV, "%s manager created"% workerName)

    # Emitter API.
    def connect_nowait(self):
        connected = self._driver.connect()
        self.ui.debug(DRV, "driver connected")
        if not connected:
            raise Exception("%s: could not connect the driver"% self.workerName)

    # Emitter API.
    def fetchFolders_nowait(self):
        self.ui.debug(DRV, "starting fetch of folders")
        self._folders = self._driver.getFolders()

    # Emitter API
    def getFolders(self):
        self.ui.debug(DRV, "folders: %s"% self._folders)
        return self._folders

    # Emitter API.
    def startDriver(self, typeName):
        # Retrieve the driver class from the type.
        cls_type = self._rascal.getTypeClass(typeName)
        self._cls_driver = cls_type.driver

        # Sanity check.
        if not issubclass(self._cls_driver, DriverInterface):
            raise Exception("driver class %s does not satisfy DriverInterface"%
                self._cls_driver.__name__)

        self.ui.debug(DRV, "starting driver '%s' of '%s'"%
            (self._cls_driver.__name__, typeName))
        self._driver = self._cls_driver()


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
    return emitter, receiver, driverName
