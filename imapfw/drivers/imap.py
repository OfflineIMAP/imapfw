# The MIT License (MIT).
# Copyright (c) 2015, Nicolas Sebrecht & contributors.

from imapfw.imap import Imap as ImapBackend
from imapfw.interface import adapts, checkInterfaces

from .driver import Driver, DriverInterface

# Annotations.
from imapfw.imap import SearchConditions, FetchAttributes
from imapfw.types.folder import Folders, Folder
from imapfw.types.message import Messages


#TODO: remove "reverse" later: the DriverInterface must define all the
# interfaces of this object.
@checkInterfaces(reverse=False)
@adapts(DriverInterface)
class Imap(Driver):
    """The Imap driver, possibly redefined by the rascal."""

    local = False

    def __init__(self, *args):
        super(Imap, self).__init__(*args)
        self.imap = ImapBackend(self.conf.get('backend'))

    def connect(self):
        host = self.conf.get('host')
        port = int(self.conf.get('port'))
        return self.imap.connect(host, port)

    def getCapability(self):
        return self.imap.getCapability()

    def getFolders(self) -> Folders:
        return self.imap.getFolders()

    def getMessages(self, messages: Messages,
            attributes: FetchAttributes) -> Messages:

        return self.imap.getMessages(messages, attributes)

    def getNamespace(self):
        return self.imap.getNamespace()

    def login(self) -> None:
        user = self.conf.get('username')
        password = self.conf.get('password')
        return self.imap.login(user, password)

    def logout(self) -> None:
        self.imap.logout()

    def searchUID(self, conditions: SearchConditions=SearchConditions()):
        return self.imap.searchUID(conditions)

    def select(self, folder: Folder) -> None:
        return self.imap.select(folder)

    #def append(self, server,  mail):
        #response = server.append(mail)
        #return response

    #def update(self, server, mail):
        #response = server.update(mail)
        #return response

    #def fetch(self, server, uids):
        #response = server.fetch(uids)
        #return response
