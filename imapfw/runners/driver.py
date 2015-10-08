
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
        callerEmitter.interruptAll(str(e))

    #def what():
        ##TODO: reuse the connectionWorker in the first folder worker.

        ## The account class is defined in the rascal.
        #cls_account = self._rascal.getAccountClass(accountName)

        ## Connect the drivers first.
        #self._left.connect()
        #self._right.connect()

        ##TODO: use the engine for this account as defined in the rascal.
        #engine = cls_account.engine()
        #engine.run()
        ## Get the folders from both ends.
        #folders = self._engine.mergeFolders()

