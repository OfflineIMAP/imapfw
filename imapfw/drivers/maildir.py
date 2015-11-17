# The MIT License (MIT)
#
# Copyright (c) 2015, Nicolas Sebrecht & contributors
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import os

from imapfw import runtime
from imapfw.toolkit import expandPath
from imapfw.error import DriverFatalError
from imapfw.constants import DRV
from imapfw.types.folder import Folders, Folder
from imapfw.interface import adapts, checkInterfaces

from .driver import Driver, DriverInterface



#TODO: remove this later: the DriverInterface must define the interfaces of
# this object.
@checkInterfaces(reverse=False)
@adapts(DriverInterface)
class Maildir(Driver):
    """Exposed Maildir driver, possibly redefined by the rascal."""

    local = True

    def __init__(self, *args):
        super(Maildir, self).__init__(*args)
        self._folders = None

    def _debug(self, msg):
        runtime.ui.debugC(DRV, "driver of %s %s"% (self.getRepositoryName(), msg))

    def _recursiveScanMaildir(self, relativePath=None):
        """Scan the Maildir recusively.

        Updates self._folders with what is found in the configured maildir path.
        TODO: fix encoding.

        :args:
        - maildirPath: path to the Maildir (as defined in the conf).
        """

        def isFolder(path):
            return (os.path.isdir(os.path.join(path, 'cur')) and
                os.path.isdir(os.path.join(path, 'new')) and
                os.path.isdir(os.path.join(path, 'tmp'))
                )

        def scanChildren(path, relativePath):
            for directory in os.listdir(path):
                if directory in ['cur', 'new', 'tmp']:
                    continue # Ignore special directories ASAP.

                folderPath = os.path.join(path, directory)
                if not os.path.isdir(folderPath):
                    continue

                if relativePath is None:
                    newRelativePath = directory
                else:
                    newRelativePath = os.path.join(relativePath, directory)

                self._recursiveScanMaildir(newRelativePath) # Recurse!

        # Fix local variables to their default values if needed.
        maildirPath = self.conf.get('path')
        sep = self.conf.get('sep')

        # Set the fullPath.
        if relativePath is None:
            fullPath = maildirPath
        else:
            fullPath = os.path.join(maildirPath, relativePath)

        if isFolder(fullPath):
            #TODO: get encoding from conf.
            if relativePath is None:
                # We are the root of the maildir. Fix the name to '/'.
                folder = Folder('/', encoding='UTF-8')
            else:
                # Fix separator to '/' ASAP. ,-)
                folder = Folder('/'.join(relativePath.split(sep)), encoding='UTF-8')
            self._folders.append(folder)

            if sep == '/': # Recurse if nested folders are allowed.
                scanChildren(fullPath, relativePath)
        else:
            # The maildirPath as given by the user might not be a real maildir
            # but a base path of maildirs. Scan this path.
            if relativePath is None:
                scanChildren(fullPath, relativePath)

    def connect(self):
        path = expandPath(self.conf.get('path'))
        try:
            os.mkdir(path)
        except FileExistsError:
            pass
        except FileNotFoundError:
            raise DriverFatalError(
                "parent directory of '%s' does not exists"% path)
        if not os.path.isdir(path):
            raise DriverFatalError("path is not a directory: %s"% path)
        self.conf['path'] = path # Record expanted path.
        return True

    def getFolders(self):
        self._folders = Folders() # Erase whatever we had.
        self._debug('scanning folders')
        self._recursiveScanMaildir() # Put result into self._folders.
        return self._folders

    def select(self, mailbox):
        #TODO
        return True

    def logout(self):
        self._debug('logging out')
