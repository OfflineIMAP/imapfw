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


class DriverArchitectInterface(object):
    def getEmitter(self):   raise NotImplementedError
    def stop(self):         raise NotImplementedError
    def kill(self):         raise NotImplementedError
    def start(self):        raise NotImplementedError


class DriverArchitect(DriverArchitectInterface):
    """Architect to manage a driver worker."""

    def __init__(self, workerName: str):
        self._workerName = workerName

        self._emitter = None
        self._worker = None
        self._name = self.__class__.__name__

        self._debug("__init__(%s)"% workerName)

    def _debug(self, msg):
        runtime.ui.debugC(ARC, "%s %s"% (self._workerName, msg))

    def getEmitter(self):
        self._debug("getEmitter()")
        return self._emitter

    def stop(self):
        self._debug("stop()")
        self._emitter.stopServing()
        self._worker.join()

    def kill(self):
        self._debug("kill()")
        self._emitter.stopServing()
        self._worker.kill()

    def start(self):
        self._debug("start()")

        receiver, self._emitter = newEmitterReceiver(self._workerName)
        driverRunner = DriverRunner(self._workerName, receiver)

        self._worker = runtime.concurrency.createWorker(self._workerName,
            topRunner,
            (self._workerName, driverRunner.run)
            )

        self._worker.start()
