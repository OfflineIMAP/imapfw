
from .driver import DriverInterface
import time

class Maildir(DriverInterface):
    def connect(self):
        # TODO: create the directory
        time.sleep(3) # simulate long time
        return True

    def getFolders(self):
        time.sleep(1) # simulate long time
        return ['a', 'b', 'x']
