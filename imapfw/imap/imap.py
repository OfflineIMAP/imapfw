# The MIT License (MIT).
# Copyright (c) 2015, Nicolas Sebrecht & contributors.

"""

Backends that implement IMAP protocol.

Don't expose IMAP states and other low-level IMAP issues. The Imap driver
doesn't care at all.

"""

from importlib import import_module

from imapfw import runtime
from imapfw.constants import IMAP
from imapfw.types.folder import Folders, Folder
from imapfw.types.message import Messages, Message

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


class FetchAttributes(object):
    def __init__(self):
        self.attributes = []

    def _enable(self, name: str) -> None:
        if not name in self.attributes:
            self.attributes.append(name)

    def enableFLAGS(self):
        self._enable('FLAGS')

    def enableUID(self):
        self._enable('UID')

    def enableINTERNALDATE(self):
        self._enable('INTERNALDATE')

    def setDefaults(self):
        self.enableUID()
        self.enableFLAGS()
        self.enableINTERNALDATE()

    def __str__(self):
        if len(self.attributes) < 1:
            raise ImapInternalError("attributes is empty")
        return "(%s)"% ' '.join(self.attributes)


#TODO: interface
class SearchConditions(object):
    def __init__(self):
        self.maxSize = None # in bytes (2097152 for 2MB)
        self.minDate = None # time_struct
        self.minUID = None

    def setMaxSize(self, maxSize: int) -> None:
        self.maxSize = maxSize

    def setMinUID(self, minUID: int) -> None:
        self.minUID = minUID

    def formatConditions(self) -> str:
        searchConditions = []

        if self.minUID is not None:
            searchConditions.append("UID %i:*"% self.minUID)

        # if self.minDate is not None:
            # searchConditions.append("SINCE %02i-%s-%i"%
                # (time_struct[2], imaplib2.MonthNames[time_struct[1]], time_struct[0]))

        if self.maxSize is not None:
            searchConditions.append("SMALLER %i"% self.maxSize)

        if len(searchConditions) > 0:
            return ' '.join(searchConditions)
        return 'UID 1:*'


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

    def connect(self, host: str, port: str) -> None:
        from .imaplib3 import imaplib2

        self.imap = imaplib2.IMAP4(host, port, debug=3, timeout=2)

    def getCapability(self) -> List[str]:
        # (typ, [data])
        # e.g. ('OK', [b'IMAP4rev1 LITERAL+'])
        response = self.imap.capability()
        self._debugResponse("getCapability", response)
        status, lst_capability = response

        str_capability = lst_capability[0].decode(ENCODING)
        capability = []
        for cap in str_capability.split(' '):
            capability.append(cap)

        self._debug("getCapability", capability)
        return capability

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

    def getMessages(self, messages: Messages,
            attributes: FetchAttributes) -> Messages:
        self._debug("getMessages", repr(messages))

        # (typ, [data, ...])
        # e.g. ('OK', [b'1 (UID 1 FLAGS (\\Seen) INTERNALDATE "15-Nov-2015
        # 00:00:46 +0100")', b'2 (UID 2 FLAGS () INTERNALDATE "15-Nov-2015
        # 00:00:46 +0100")'])
        response = self.imap.uid('FETCH', messages.coalesceUIDs(),
            str(attributes))
        self._debugResponse("getMessages", response)

        status, data = response
        if status == 'OK':
            for item in data:
                item = item.decode(ENCODING)
                uid = int(item[0])
                #TODO: item must be of type MessageAttributes.
                messages.setAttributes(uid, item)
            return messages
        raise ImapCommandError(data)

    def getNamespace(self):
        return self.imap.namespace()

    def login(self, user: str, password: str) -> None:
        self._debug("login", "%s, <password>"% user)

        # (typ, [data])
        # e.g. ('OK', [b'Logged In'])
        response = self.imap.login(user, password)
        self._debugResponse("capability", response)

        status, data = response
        if status == 'OK':
            return None

        data = data.decode(ENCODING)
        raise ImapCommandError(data)

    def logout(self) -> None:
        self.imap.logout()

    def searchUID(self, searchConditions: SearchConditions=SearchConditions()):
        conditions = searchConditions.formatConditions()
        self._debug("searchUID", "%s"% conditions)

        # (typ, [data])
        # e.g. ('OK', [b'2']
        response = self.imap.uid('SEARCH', conditions)
        self._debugResponse("searchUID", response)
        status, data = response
        if status == 'OK':
            messages = Messages()
            for uid in data[0].decode(ENCODING).split(' '):
                messages.add(Message(int(uid)))
            return messages

        data = data.decode(ENCODING)
        raise ImapCommandError(data)

    def select(self, folder: Folder) -> int:
        """Return number of existing messages."""

        self._debug("select", str(folder))
        # (typ, [data])
        # e.g. ('OK', [b'1 2'])
        response = self.imap.select(folder.getName())
        self._debugResponse("select", response)

        status, data = response
        if status == 'OK':
            #TODO: make a collection of UIDs.
            return int(data[0])

        data = data.decode(ENCODING)
        raise ImapCommandError(data)


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
