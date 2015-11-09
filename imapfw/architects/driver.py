# The MIT License (MIT)
#
# Copyright (c) 2015, Nicolas Sebrecht & contributors
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from imapfw import runtime
from imapfw.constants import ARC
from imapfw.edmp import newEmitterReceiver
from imapfw.runners import DriverRunner, topRunner

from .debug import debugArchitect

# Interfaces.
from imapfw.interface import implements, Interface
# Annotations.
from imapfw.edmp import Emitter


class DriverArchitectInterface(object):
    def _debug(self, msg) -> None:
        """Debug."""

    def getEmitter(self) -> Emitter:
        """Return the emitter for the driver."""

    def init(self) -> None:
        """Initialize object."""

    def kill(self) -> None:
        """Kill the driver."""

    def start(self) -> None:
        """Start the driver."""

    def stop(self) -> None:
        """Stop the driver."""

@debugArchitect
@implements(DriverArchitectInterface)
class DriverArchitect(object):
    """Architect to manage a driver worker."""

    def __init__(self, workerName: str):
        self.workerName = workerName

        self.emitter = None
        self.worker = None
        self.name = self.__class__.__name__

        self._debug("__init__(%s)"% workerName)

    def _debug(self, msg) -> None:
        runtime.ui.debugC(ARC, "%s %s"% (self.workerName, msg))

    def getEmitter(self) -> Emitter:
        self._debug("getEmitter()")
        assert self.emitter is not None
        return self.emitter

    def init(self) -> None:
        receiver, self.emitter = newEmitterReceiver(self.workerName)
        driverRunner = DriverRunner(self.workerName, receiver)

        self.worker = runtime.concurrency.createWorker(self.workerName,
            topRunner,
            (self.workerName, driverRunner.run)
            )

    def kill(self) -> None:
        self._debug("kill()")
        self.emitter.stopServing()
        self.worker.kill()

    def start(self) -> None:
        self._debug("start()")
        self.worker.start()

    def stop(self) -> None:
        self._debug("stop()")
        self.emitter.stopServing()
        self.worker.join()


@implements(DriverArchitectInterface)
class ReuseDriverArchitect(DriverArchitect):
    def __init__(self, emitter: Emitter):
        self.emitter = emitter

    def _debug(self, msg) -> None:
        super(ReuseDriverArchitect, self)._debug(msg)

    def getEmitter(self) -> Emitter:
        return self.emitter

    def init(self) -> None:
        pass

    def kill(self) -> None:
        self.emitter.stopServing()

    def start(self) -> None:
        pass

    def stop(self) -> None:
        self.emitter.stopServing()


class DriversArchitectInterface(Interface):
    """Manage driver architects."""

    scope = Interface.INTERNAL

    def getEmitter(self, number: int) -> Emitter:
        """Return the emitter for given number."""

    def init(self) -> None:
        """Setup and start end-drivers."""

    def kill(self) -> None:
        """Kill the workers."""

    def start(self) -> None:
        """Start the workers."""

    def stop(self) -> None:
        """Stop the workers."""

@implements(DriversArchitectInterface)
class DriversArchitect(object):
    def __init__(self, workerName: str, number: int):
        self.workerName = workerName
        self.number = number

        self.driverArchitects = {}

    def getEmitter(self, number: int) -> Emitter:
        return self.driverArchitects[number].getEmitter()

    def init(self) -> None:
        for i in range(self.number):
            workerName = "%s.Driver.%i"% (self.workerName, i)
            driver = DriverArchitect(workerName)
            driver.init()
            self.driverArchitects[i] = driver

    def kill(self) -> None:
        for architect in self.driverArchitects.values():
            architect.kill()

    def start(self) -> None:
        for architect in self.driverArchitects.values():
            architect.start()

    def stop(self) -> None:
        for architect in self.driverArchitects.values():
            architect.stop()
