

class ActionInterface(object):

    honorHooks = True
    requireRascal = True

    def exception(self, e):     raise NotImplementedError
    def getExitCode(self):      raise NotImplementedError
    def init(self, ui, concurrency, rascal, actionOptions):
        """Configure the environement right after the object is created."""
        raise NotImplementedError
    def run(self):              raise NotImplementedError
