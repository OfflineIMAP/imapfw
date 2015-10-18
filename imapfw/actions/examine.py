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

from .interface import ActionInterface

from ..types.repository import RepositoryBase
from ..controllers.examine import ExamineController
from ..drivers.driver import DriverInterface

class Examine(ActionInterface):
    """Examine repositories (all run sequentially)."""

    honorHooks = False
    requireRascal = True

    def __init__(self):
        self._exitCode = 0
        self._ui = None
        self._rascal = None
        self._concurrency = None

        self._architects = []

    def exception(self, e):
        self._exitCode = 3

    def getExitCode(self):
        return self._exitCode

    def init(self, ui, concurrency, rascal, options):
        self._ui = ui
        self._concurrency = concurrency
        self._rascal = rascal

    def run(self):
        repositories = self._rascal.getAll([RepositoryBase])

        for repository in repositories:
            if isinstance(repository, DriverInterface):
                continue
            try:
                repository.fw_init(self._ui)
                repository.fw_addController(ExamineController)
                driver = repository.fw_chainControllers()
                driver.fw_init(self._ui, repository.conf, None)

                self._ui.info("# Repository %s (type %s)"%
                    (repository.getName(), driver.getName()))
                self._ui.info("")
                self._ui.info("controllers: %s"% repository.controllers)
                self._ui.info("")

                driver.connect()
                driver.getFolders()
                self._ui.info("")
            except Exception as e:
                raise
                self._ui.warn("got %s %s"% (repr(e), str(e)))
