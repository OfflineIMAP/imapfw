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

"""

The achitects are high level objects to support actions with dynamic process
handling.

They are helpers.

"""

from imapfw import runtime

from .driver import DriversArchitect
from .debug import debugArchitect

# Interfaces.
from imapfw.interface import Interface, implements

# Annotations.
from imapfw.concurrency import Queue
from imapfw.edmp import Emitter
from imapfw.annotation import Function


class ArchitectInterface(Interface):
    scope = Interface.INTERNAL

    def _getWorkerName(self) -> str:
        """Return worker name."""

    def kill(self) -> None:
        """Kill worker."""

    def start(self, runner: Function, runnerArgs: tuple) -> None:
        """Start worker."""

    def stop(self) -> None:
        """Stop worker."""

@debugArchitect
@implements(ArchitectInterface)
class Architect(object):
    def __init__(self, workerName: str):
        self.workerName = workerName

        self.name = self.__class__.__name__
        self.worker = None

    def _getWorkerName(self) -> str:
        return self.workerName

    def kill(self) -> None:
        self.worker.kill()

    def start(self, runner: Function, runnerArgs: tuple) -> None:
        self.worker = runtime.concurrency.createWorker(
            self.workerName, runner, runnerArgs)
        self.worker.start()

    def stop(self) -> None:
        self.worker.join()


class EngineArchitectInterface(Interface):
    """Architect for running an engine with both side drivers.

    Aggragate the engine architect and the drivers."""

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
