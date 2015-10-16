

from ..constants import ARC

from ..managers.driver import DriverManager
from ..runners.driver import driverRunner


class DriverArchitectInterface(object):
    def getEmitter(self):   raise NotImplementedError
    def join(self):         raise NotImplementedError
    def kill(self):         raise NotImplementedError
    def start(self):        raise NotImplementedError


#TODO: decorator to catch all errors and raise DriverFatalError.
class DriverArchitect(object):
    """Architect to seup the driver manager."""
    def __init__(self, ui, concurrency, rascal):
        self._ui = ui
        self._concurrency = concurrency
        self._rascal = rascal

        self._emitter = None
        self._receiver = None

    def getEmitter(self):
        return self._emitter

    def join(self):
        self._receiver.join()

    def kill(self):
        self._receiver.kill()

    def start(self, workerName, callerEmitter):
        self._ui.debugC(ARC, "starting driver manager '{}'", workerName)

        driverManager = DriverManager(
            self._ui,
            self._concurrency,
            workerName,
            self._rascal,
            )
        self._emitter, self._receiver = driverManager.split()

        self._receiver.start(driverRunner, (
            self._ui,
            workerName,
            self._receiver,
            callerEmitter,
            ))
