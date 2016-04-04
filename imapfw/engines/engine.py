# The MIT License (MIT).
# Copyright (c) 2015-2016, Nicolas Sebrecht & contributors.

"""

Engines are users of the the drivers. The logic to apply to the data is put in
the engines, e.g. a 3-way merge engine. They are likely put in their own worker
and should mostly send events to work "with the outside" (the other workers).

Engines might be rather complex. Hence, they aren't meant at being exposed in
the rascal and best practices must be applied to the code.

Engines follows the components design pattern because factoring engine code is
not easy.

IOW, engines here are meant to be parent objects. Each is a pure data container
and provide some default processing code for the behaviour. It is the component.

Good components modeling seperate each related data into one simple and
dedicated component which is easy to re-use. Combine compenents into object
(called entities) to use them in the application.

"""

from imapfw import runtime

#TODO: engines debug logs.
from imapfw.constants import WRK

# Interfaces.
from imapfw.interface import Interface, implements, checkInterfaces

# Annotations.
from imapfw.edmp import Emitter
from imapfw.concurrency import Queue


class EngineInterface(Interface):

    scope = Interface.INTERNAL

    def run(self, taskQueue: Queue) -> None:
        """Run the engine."""


class SyncEngineInterface(Interface):

    scope = Interface.INTERNAL

    def checkExitCode(self) -> None:
        """Check exit code."""

    def debug(self, msg: str) -> None:
        """Debug logging."""

    def getExitCode(self) -> int:
        """Get exit code."""

    def processing(self, task: str) -> None:
        """Log what is processed by the engine."""

    def setExitCode(self, exitCode: int) -> None:
        """Set exit code."""


@checkInterfaces()
@implements(SyncEngineInterface)
class SyncEngine(object):
    def __init__(self, workerName: str):
        self._exitCode = -1 # Force the run to set a valid exit code.
        self._gotTask = False
        self.workerName = workerName

    def checkExitCode(self) -> None:
        if self._gotTask is False:
            self.setExitCode(0)
        else:
            if self._exitCode < 0:
                runtime.ui.critical("%s exit code was not set correctly"%
                    self.workerName)
                self.setExitCode(99)

    def debug(self, msg: str) -> None:
        runtime.ui.debugC(WRK, "%s: %s"% (self.workerName, msg))

    def getExitCode(self) -> int:
        return self._exitCode

    def processing(self, task: str) -> None:
        runtime.ui.infoL(2, "%s processing: %s"% (self.workerName, task))
        self._gotTask = True

    def setExitCode(self, exitCode: int) -> None:
        if exitCode > self._exitCode:
            self._exitCode = exitCode
