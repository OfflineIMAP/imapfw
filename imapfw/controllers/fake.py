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

from .controller import Controller

from imapfw.types.folder import Folders, Folder


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
        # Force to redefine all the driver and controller APIs.
        raise AttributeError("no attribute %s"% name)

    def _folders(self):
        folders = Folders()
        for folderName in self.conf.get('folders'):
            folders.append(Folder(folderName))
        return folders

    def connect(self):
        return True

    def fetchFolders(self):
        return self._folders()

    def getFolders(self):
        return self._folders()

    def getClassName(self):
        return self.__class__.__name__

    def getDriverClassName(self):
        return self.getClassName()

    def getRepositoryName(self):
        return self.repositoryName

    def init(self):
        pass

    def isLocal(self):
        return self.isLocal

    def logout(self):
        return True

    def select(self, folder):
        return True
