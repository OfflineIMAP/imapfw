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

from .driver import Driver

from imapfw.imap.imap import Imap as ImapBackend
from imapfw.types.folder import Folder, Folders


class Imap(Driver):
    """Imap driver possibly redefined by the rascal."""

    isLocal = False

    def __init__(self, *args):
        super(Imap, self).__init__(*args)
        self.imap = ImapBackend(self.conf.get('backend'))
        self.imap.configure()

    def connect(self):
        #TODO: if already connected, pass.
        return True
        #return self.imap.connect(host, port)

    def getFolders(self):
        return Folders(Folder(b'on'), Folder(b'imap'), Folder(b'side'))

    def select(self, mailbox):
        #TODO
        return True

    def logout(self):
        #self.imap.logout()
        pass

    #def append(self, server,  mail):
        #response = server.append(mail)
        #return response

    #def update(self, server, mail):
        #response = server.update(mail)
        #return response

    #def fetch(self, server, uids):
        #response = server.fetch(uids)
        #return response
