

from .interface import ActionInterface


class Noop(ActionInterface):
    """The noop action allows testing the loading of the rascal."""

    def exception(self, e):
        raise

    def getExitCode(self):
        return 0

    def initialize(self, ui, rascal, actionOptions):
        pass

    def run(self):
        pass
