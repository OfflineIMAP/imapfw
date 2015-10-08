
from ..concurrency.concurrency import Concurrency
from ..constants import WRK


def setupConcurrency(ui, rascal):
    """Helper function to setup concurrency."""


    backendName = 'multiprocessing'
    try:
        backendName = rascal.getConcurrencyBackendName()
    except KeyError:
        ui.error("concurrency backend not configured, "
            "fallbacking to multiprocessing")
    concurrency = Concurrency(backendName)
    ui.setCurrentWorkerNameFunction(concurrency.getCurrentWorkerNameFunction())
    ui.debug(WRK, "using backend %s"% backendName)

    # Turn ui into thread-safe mode.
    ui.setLock(concurrency.createLock())
    ui.debug(WRK, "ui backend made thread-safe")

    # Turn ui into thread-safe mode.
    rascal.setLock(concurrency.createLock())
    ui.debug(WRK, "rascal made thread-safe")

    # The rascal must use the thread-safe ui, too!
    rascal.configure(ui)

    return ui, rascal, concurrency
