
"""

Define runners for the workers.

"""

import traceback

from ..constants import WRK



def driverRunner(ui, workerName, controller):
    """The "proteted" runner for a driver controller."""

    try:
        if not driver.initialize(): # Initialize the driver and connect.
            raise DriverError("driver cannot connect")
        while not driver.stopNow():
            driver.serve_nowait() # Relay controller requests.
    except DriverError as e:
        ui.critical("could not initialize driver")
    except Exception as e:
        ui.critical("%s got Exception %s", workerName, str(e))
        # No!
        controller.interruptAll(str(e))
    finally:
        ui.debug(WRK, "runner ended")
        controller.declareStopped() # Stop serving this worker!


def ConsumerRunner(runner, emitter):
    try:
        ui = runner.getUIinst()
        workerName = runner.getWorkerName()

        while True:
            try:
                task =  runner.getTask()
                if task is None: # No more task.
                    break # Quit the consumer loop.

                runner.consume(task)
                ui.debug(WRK, "got task %s"% task)

            except KeyboardInterrupt:
                raise

            # Handle exceptions we can safely ignore.
            except Exception as e:
                ui.error('%s exception occured: %s\n%s',
                    workerName, e, traceback.format_exc())
                raise

        emitter.stopServing()
        ui.debug(WRK, "runner ended")
    except Exception as e:
        ui.critical("%s got Exception", workerName)
        emitter.interruptAll(str(e))

