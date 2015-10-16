

from .interface import ActionInterface


class Noop(ActionInterface):
    """The noop action allows testing the loading of the rascal."""

    honorHooks = False
    requireRascal = False

    def exception(self, e):
        raise

    def getExitCode(self):
        return 0

    def init(self, ui, concurrency, rascal, actionOptions):
        pass

    def run(self):
        pass
