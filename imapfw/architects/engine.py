# The MIT License (MIT).
# Copyright (c) 2016, Nicolas Sebrecht & contributors.

"""

Architect for basic engine.

"""

from .architect import Architect
from .driver import DriversArchitect

from .debug import debugArchitect

# Interfaces.
from imapfw.interface import Interface, implements, checkInterfaces

# Annotations.
from imapfw.edmp import Emitter
from imapfw.annotation import Function


class EngineArchitectInterface(Interface):
    """Architect for running an engine with both side drivers.

    Aggregate the engine architect and the drivers."""

    scope = Interface.INTERNAL

    def getLeftEmitter(self) -> Emitter:
        """Return the emitter of the left-side driver."""

    def getRightEmitter(self) -> Emitter:
        """Return the emitter of the right-side driver."""

    def init(self) -> None:
        """Initialize the architect. Helps to compose components easily."""

    def kill(self) -> None:
        """Kill workers."""

    def start(self, runner: Function, runnerArgs: tuple) -> None:
        """Start the workers."""

    def stop(self) -> None:
        """Stop workers."""

@debugArchitect
@checkInterfaces()
@implements(EngineArchitectInterface)
class EngineArchitect(object):
    def __init__(self, workerName: str):
        self.workerName = workerName

        self.architect = None
        self.drivers = None

    def getLeftEmitter(self) -> Emitter:
        return self.drivers.getEmitter(0)

    def getRightEmitter(self) -> Emitter:
        return self.drivers.getEmitter(1)

    def init(self) -> None:
        self.architect = Architect(self.workerName)
        self.drivers = DriversArchitect(self.workerName, 2)
        self.drivers.init()

    def kill(self) -> None:
        self.drivers.kill()
        self.architect.kill()

    def start(self, runner: Function, runnerArgs: tuple) -> None:
        self.drivers.start()
        self.architect.start(runner, runnerArgs)

    def stop(self) -> None:
        self.drivers.stop()
        self.architect.stop()

