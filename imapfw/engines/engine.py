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

#TODO: engines debug logs.
from imapfw.constants import WRK

# Interfaces.
from imapfw.interface import Interface, implements

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
