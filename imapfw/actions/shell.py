# The MIT License (MIT).
# Copyright (c) 2015, Nicolas Sebrecht & contributors.

from imapfw import runtime
from imapfw.shells import Shell
from imapfw.interface import implements, checkInterfaces
from imapfw.conf import Parser

from .interface import ActionInterface

# Annotations.
from imapfw.annotation import ExceptionClass


@checkInterfaces()
@implements(ActionInterface)
class ShellAction(object):
    """Run in (interactive) shell mode."""

    honorHooks = False
    requireRascal = True

    def __init__(self):
        self._shellName = None
        self._repositoryName = None
        self._exitCode = -1

    def _setExitCode(self, exitCode):
        if exitCode > self._exitCode:
            self._exitCode = exitCode

    def exception(self, e: ExceptionClass) -> None:
        self.exitCode = 3
        raise NotImplementedError #TODO

    def getExitCode(self) -> int:
        return self._exitCode

    def init(self, parser: Parser) -> None:
        self._shellName = parser.get('shell_name')

    def run(self) -> None:
        cls_shell = runtime.rascal.get(self._shellName, [Shell])
        shell = cls_shell()
        shell.beforeSession()
        shell.configureCompletion()
        shell.session()
        exitCode = shell.afterSession()
        self._setExitCode(exitCode)

actionParser = Parser.addAction('shell', ShellAction, help="run in shell mode")

actionParser.add_argument(dest="shell_name",
    default=None,
    metavar="SHELL_NAME",
    help="the shell from the rascal to run")
