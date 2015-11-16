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

"""

Backends that implement IMAP protocol.

Don't expose IMAP states and other low-level IMAP issues. The Imap driver
doesn't care at all.

"""

from importlib import import_module

from imapfw import runtime
from imapfw.constants import IMAP
from imapfw.types.folder import Folders, Folder

# Annotations.
from imapfw.annotation import List, Dict, Union

#from .imapc.interface import IMAPcInterface


#TODO: use UTF-7.
ENCODING = 'UTF-8'


# Exceptions.
class ImapInternalError(Exception):
    """Error raised for internal logic errors."""

class ImapTemporaryError(ImapInternalError):
    """Error raised for temporary IMAP protocol errors."""

class ImapCommandError(ImapInternalError):
    """Error raised when IMAP server repond with failure status to a command."""

class ImapAbortError(ImapInternalError):
    """Error raised when connexion is unexpectly closed."""


#TODO: move to imapc/interface.py
class IMAPcInterface(object):
    pass #TODO


class IMAPlib2_skater(object):
    """Allows to use imaplib2 with the API of IMAPc."""

    def __init__(self):
        self.imap = None

    def _debug(self, command: str, msg: str) -> None:
        runtime.ui.debugC(IMAP, "[%s] %s"%
            (command, msg))

    def _debugResponse(self, command: str, response: str) -> None:
        runtime.ui.debugC(IMAP, "[%s] response: %s"%
            (command, response))

    def capability(self) -> List[str]:
        capability = []

        # (typ, [data])
        # e.g. ('OK', [b'IMAP4rev1 LITERAL+'])
        response = self.imap.capability()
        self._debugResponse("capability", response)
        status, lst_capability = response

        str_capability = lst_capability[0].decode(ENCODING)
        for cap in str_capability.split(' '):
            capability.append(cap)

        self._debug("capability", capability)
        return capability

    def connect(self, host: str, port: str) -> None:
        from .imaplib3 import imaplib2

        self.imap = imaplib2.IMAP4(host, port, debug=3, timeout=2)

    def getFolders(self) -> List[Dict[str, Union[str, bool]]]:
        folders = Folders()

        # (typ, [data])
        # e.g. ('OK', [b'(\\HasNoChildren) "." INBOX.DRAFT'])
        response = self.imap.list()
        self._debugResponse('list', response)

        status, data = response
        if status == 'OK':
            for bytes_folderInfo in data:
                foldersInfo = bytes_folderInfo.decode(ENCODING)
                lst_foldersInfo = foldersInfo.split(' ')

                folderName = ' '.join(lst_foldersInfo[2:]).encode(ENCODING)
                folder = Folder(folderName)

                folder.setRoot(lst_foldersInfo[1])

                childrenInfo = lst_foldersInfo[0]
                if childrenInfo == "(\\HasNoChildren)":
                    folder.setHasChildren(False)
                else:
                    folder.setHasChildren(True)

                folders.append(folder)
            self._debug('getFolders', folders)
            return folders

        raise ImapCommandError(str(data))

    def login(self, user: str, password: str) -> None:
        self._debug("login", "%s, <password>"% user)

        # (typ, [data])
        # e.g. ('OK', [b'Logged In'])
        response = self.imap.login(user, password)
        self._debugResponse("capability", response)

        status, msg = response
        if status == 'OK':
            return None

        msg = msg.decode(ENCODING)
        raise ImapCommandError(msg)

    def logout(self) -> None:
        self.imap.logout()



def Imap(backendNameVersion):
    """Returns an IMAP instance to run IMAP commands.

    :backendNameVersion: the backend name to use like "imapc" or "imaplib2". For
        imaplib2, the version number can be appended like this: "imaplib2-2.50".
    """

    lst_nameVersion = backendNameVersion.split('-')
    backendName = lst_nameVersion.pop(0)
    version = None
    if len(lst_nameVersion) > 0:
        version = lst_nameVersion.pop(0)

    # imapc
    if backendName == 'imapc':
        from .imapc.imapc import IMAP4rev1
        return IMAP4rev1()

    # imaplib2 (pure-python3)
    if backendName == 'imaplib3':
        return IMAPlib2_skater()

    raise Exception("unkown backend: %s"% backendName)
