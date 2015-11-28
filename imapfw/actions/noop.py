# The MIT License (MIT).
# Copyright (c) 2015, Nicolas Sebrecht & contributors.

from imapfw.interface import implements

from .interface import ActionInterface

# Annotations.
from imapfw.annotation import ExceptionClass, Dict


@implements(ActionInterface)
class Noop(object):
    """The noop action allows testing the loading of the rascal."""

    honorHooks = False
    requireRascal = False

    def exception(self, e: ExceptionClass) -> None:
        raise NotImplementedError

    def getExitCode(self) -> int:
        return 0

    def init(self, options: Dict) -> None:
        pass

    def run(self) -> None:
        pass
