
import traceback
from ..constants import WRK, DRV


def driverRunner(ui, rascal, workerName, callerEmitter, driverReceiver):
    """The runner for a driver."""

    try:
        try:
            ui.debug(DRV, "starts serving")
            while driverReceiver.serve_nowait():
                pass
            ui.debug(DRV, "stopped serving")

        except KeyboardInterrupt:
            raise

        except Exception as e:
            ui.error('%s exception occured: %s\n%s',
                workerName, e, traceback.format_exc())
            raise

        ui.debug(WRK, "runner ended")
    except Exception as e:
        ui.critical("%s got Exception", workerName)
        callerEmitter.unkownInterruptionError(str(e))
