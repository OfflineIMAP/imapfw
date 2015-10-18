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
