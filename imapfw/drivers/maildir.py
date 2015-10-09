
import time
import os

from .driver import DriverBase

from ..util.toolkit import expandPath
from ..error import DriverFatalError


class Maildir(DriverBase):
    def connect(self):
        path = expandPath(self.conf.get('path'))
        try:
            os.mkdir(path)
        except FileExistsError:
            pass
        except FileNotFoundError:
            raise DriverFatalError(
                "parent directory of '%s' does not exists"% path)

        time.sleep(3) # simulate long time
        return True

    def getFolders(self):
        time.sleep(1) # simulate long time
        return ['a', 'b', 'x']
