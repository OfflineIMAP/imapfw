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

from .interface import ActionInterface

from imapfw.types.account import Account, loadAccount
from imapfw.controllers.examine import ExamineController
from imapfw.drivers.driver import DriverInterface

class Examine(ActionInterface):
    """Examine repositories (all run sequentially)."""

    honorHooks = False
    requireRascal = True

    def __init__(self):
        self._exitCode = 0
        self.ui = runtime.ui

        self._architects = []

    def exception(self, e):
        self._exitCode = 3

    def getExitCode(self):
        return self._exitCode

    def init(self, options):
        pass

    def run(self):
        class Report(object):
            def __init__(self):
                self._number = 0
                self.content = {}

            def _getNumber(self):
                self._number += 1
                return self._number

            def line(self, line: str=''):
                self.content[self._getNumber()] = ('line', (line,))

            def list(self, elements: list=[]):
                self.content[self._getNumber()] = ('list', (elements,))

            def title(self, title: str, level: int=1):
                self.content[self._getNumber()] = ('title', (title, level))

            def markdown(self):
                for lineDef in self.content.values():
                    kind, args = lineDef

                    if kind == 'title':
                        title, level = args
                        prefix = '#' * level
                        print("\n%s %s\n"% (prefix, title))

                    if kind == 'list':
                        for elem in args[0]:
                            print("* %s"% elem)

                    if kind == 'line':
                        print(args[0])


        cls_accounts = runtime.rascal.getAll([Account])

        repositories = []
        for cls_account in cls_accounts:
            account = loadAccount(cls_account)
            repositories.append(account.fw_getLeft())
            repositories.append(account.fw_getRight())

        report = Report()
        for repository in repositories:
            if isinstance(repository, DriverInterface):
                continue
            try:
                repository.fw_insertController(ExamineController,
                    {'report': report})
                driver = repository.fw_getDriver()

                report.title("Repository %s (driver %s)"%
                    (repository.getClassName(), driver.getDriverClassName()))
                report.line("controllers: %s"%
                    [x.__name__ for x in repository.controllers])

                driver.connect()
                driver.getFolders()

                report = driver.fw_getReport()
            except Exception as e:
                raise
                self.ui.warn("got %s %s"% (repr(e), str(e)))
        report.markdown()
