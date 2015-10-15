
from .driver import DriverBase

from ..imap.imap import Imap as ImapBackend


class Imap(DriverBase):
    """Imap driver possibly redefined by the rascal."""

    isLocal = False

    def fw_initialize(self, ui, conf, owner):
        super(Imap, self).fw_initialize(ui, conf, owner)

        # Assume fw_loadConf() was already called.
        self.imap = ImapBackend(self.conf.get('backend'))
        self.imap.configure(self.ui)

    def connect(self):
        return True
        #return self.imap.connect(host, port)

    def getFolders(self):
        return ['on', 'imap', 'side']

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
