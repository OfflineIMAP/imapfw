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


class Imap(Driver):
    """Imap driver possibly redefined by the rascal."""

    isLocal = False

    def __init__(self, *args):
        super(Imap, self).__init__(*args)
        self.imap = ImapBackend(self.conf.get('backend'))

    def capability(self):
        return self.imap.capability()

    def connect(self):
        host = self.conf.get('host')
        port = int(self.conf.get('port'))
        return self.imap.connect(host, port)

    def getFolders(self):
        return self.imap.getFolders()

    def select(self, mailbox):
        #TODO
        return True

    def login(self) -> None:
        user = self.conf.get('username')
        password = self.conf.get('password')
        return self.imap.login(user, password)

    def logout(self) -> None:
        self.imap.logout()

    #def append(self, server,  mail):
        #response = server.append(mail)
        #return response

    #def update(self, server, mail):
        #response = server.update(mail)
        #return response

    #def fetch(self, server, uids):
        #response = server.fetch(uids)
        #return response
