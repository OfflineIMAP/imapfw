# The MIT License (MIT).
# Copyright (c) 2015, Nicolas Sebrecht & contributors.

from imapfw import runtime
from imapfw.interface import implements

from .interface import ActionInterface

# Annotations.
from imapfw.annotation import ExceptionClass, Dict


@implements(ActionInterface)
class Devel(object):
    """For development purpose only."""

    honorHooks = False
    requireRascal = True

    def __init__(self):
        self._exitCode = 0

        self.ui = runtime.ui
        self.concurrency = runtime.concurrency
        self.rascal = runtime.rascal
        self._options = {}

    def exception(self, e: ExceptionClass) -> None:
        self._exitCode = 3

    def getExitCode(self) -> int:
        return self._exitCode

    def init(self, options: Dict) -> None:
        self._options = options

    def run(self) -> None:
        self.ui.infoL(1, 'running devel action')

        from ..imap.imap import Imap

        imap = Imap('imaplib2-2.50')
        imap.configure(self.ui)
        imap.connect('127.0.0.1', 10143)
        imap.logout()
