

class ActionInterface(object):
    def exception(self, e):
        raise NotImplementedError

    def getExitCode(self):
        raise NotImplementedError

    def initialize(self, ui, concurrency, rascal, actionOptions):
        """Configure the environement right after the object is created."""
        raise NotImplementedError

    def run(self):
        raise NotImplementedError
