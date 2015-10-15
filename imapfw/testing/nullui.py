
class NullUI(object):
    def critical(self, *args): pass
    def debug(self, *args): pass
    def debugC(self, category, *args): pass
    def error(self, *args): pass
    def exception(self, *args): pass
    def format(self, *args): pass
    def info(self, *args): pass
    def infoL(self, level, *args): pass
    def setInfoLevel(self, level): pass
    def warn(self, *args): pass
