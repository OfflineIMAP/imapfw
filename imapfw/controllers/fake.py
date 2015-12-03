# The MIT License (MIT).
# Copyright (c) 2015, Nicolas Sebrecht & contributors.

from imapfw.types.folder import Folders, Folder
from imapfw.types.message import Messages, Message

from .controller import Controller


class FakeDriver(Controller):

    conf = None

    ImapConf = {
        'folders': [b'INBOX', b'INBOX/spam', b'INBOX/outbox',
            b'INBOX/sp&AOk-cial',
        ]
    }

    MaildirConf = {
        'folders': [b'INBOX', b'INBOX/maidir_archives']
    }

    def __getattr__(self, name):
        if name.startswith('fw_'):
            return getattr(self.driver, name)
        message = ("FakeDriver %s did not handle call to '%s'"%
                (self.getClassName(), name))
        raise AttributeError(message)

    def _folders(self):
        folders = Folders()
        for folderName in self.conf.get('folders'):
            folders.append(Folder(folderName))
        return folders

    def connect(self):
        return True

    def getCapability(self):
        return ["TODO=CAPABILITY"] #TODO

    def getClassName(self):
        return self.__class__.__name__

    def getDriverClassName(self):
        return self.driver.getClassName()

    def getFolders(self):
        return self._folders()

    def getNamespace(self):
        return "TODO" #TODO

    def getRepositoryName(self):
        return self.repositoryName

    def init(self):
        pass

    def isLocal(self):
        return self.driver.isLocal()

    def login(self):
        return True

    def logout(self):
        return True

    def search(self, conditions):
        return Messages() #TODO

    def select(self, folder):
        return True #TODO
