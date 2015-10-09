
from .driver import DriverBase


class Imap(DriverBase):
    def append(self, server,  mail):
        response = server.append(mail)
        return response

    def update(self, server, mail):
        response = server.update(mail)
        return response

    def fetch(self, server, uids):
        response = server.fetch(uids)
        return response
