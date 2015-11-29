# The MIT License (MIT).
# Copyright (c) 2015, Nicolas Sebrecht & contributors.

from imapfw import runtime
from imapfw.types.account import Account, loadAccount
from imapfw.controllers.examine import ExamineController
from imapfw.drivers.driver import DriverInterface
from imapfw.interface import implements, checkInterfaces
from imapfw.conf import Parser

from .interface import ActionInterface

# Annotations.
from imapfw.annotation import ExceptionClass, Dict


@checkInterfaces()
@implements(ActionInterface)
class Examine(object):
    """Examine repositories (all run sequentially)."""

    honorHooks = False
    requireRascal = True

    def __init__(self):
        self._exitCode = 0
        self.ui = runtime.ui

        self._architects = []

    def exception(self, e: ExceptionClass) -> None:
        self._exitCode = 3

    def getExitCode(self) -> int:
        return self._exitCode

    def init(self, parser: Parser) -> None:
        pass

    def run(self) -> None:
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


Parser.addAction('examine', Examine, help="examine repositories")
