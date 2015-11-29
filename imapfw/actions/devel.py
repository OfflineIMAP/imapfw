# The MIT License (MIT).
# Copyright (c) 2015, Nicolas Sebrecht & contributors.

from imapfw import runtime
from imapfw.interface import implements, checkInterfaces
from imapfw.conf import Parser

from .interface import ActionInterface

# Annotations.
from imapfw.annotation import ExceptionClass


@checkInterfaces()
@implements(ActionInterface)
class Devel(object):
    """For development purpose only."""

    honorHooks = False
    requireRascal = True

    def __init__(self):
        self._exitCode = 0

    def exception(self, e: ExceptionClass) -> None:
        self._exitCode = 3

    def getExitCode(self) -> int:
        return self._exitCode

    def init(self, parser: Parser) -> None:
        pass

    def run(self) -> None:
        runtime.ui.infoL(1, 'running devel action')

        from ..imap.imap import Imap

        imap = Imap('imaplib2-2.50')
        imap.connect('127.0.0.1', 10143)
        imap.logout()

Parser.addAction('devel', Devel, help="development")
