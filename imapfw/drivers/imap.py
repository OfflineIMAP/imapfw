
from .driver import DriverBase

from ..constants import DRV
from ..imap.imap import Imap as ImapBackend


class Imap(DriverBase):
    """Imap driver possibly redefined by the rascal."""

    def fw_initialize(self, ui, conf):
        super(Imap, self).fw_initialize(ui, conf)

        # Assume fw_loadConf() was already called.
        self.imap = ImapBackend(self.conf.get('backend'))
        self.imap.configure(self.ui)

    def connect(self):
        host, port = self.conf.get('host'), self.conf.get('port')
        self.ui.debugC(DRV, 'connecting to {}:{}', host, port)
        return True
        #return self.imap.connect(host, port)

    def getFolders(self):
        return ['a', 'b', 'x']

    def logout(self):
        #self.imap.logout()
        self.ui.debugC(DRV, 'logged out')

    #def append(self, server,  mail):
        #response = server.append(mail)
        #return response

    #def update(self, server, mail):
        #response = server.update(mail)
        #return response

    #def fetch(self, server, uids):
        #response = server.fetch(uids)
        #return response
