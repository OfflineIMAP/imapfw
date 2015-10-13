
from importlib import import_module

from .imapc.interface import IMAPcInterface


class IMAPlib2_skater(IMAPcInterface):
    #TODO: allow to use IMAPc API with imaplib2 as backend.

    def __init__(self, version):
        self._imap = import_module(".imap.imaplib2.imaplib2_"% version, 'imapfw')


def Imap(backendName, backendVersion=None):
    # imapc
    if backendName == 'imapc':
        mod = import_module('.imap.imapc.imapc', 'imapfw')
        return mod.IMAP4rev1()

    # imaplib2
    if backendName == 'imaplib2':
        if backendVersion is None:
            backendVersion = '2_49'
        else:
            backendVersion = '_'.join('.'.split(backendVersion))

        return IMAPlib2_skater(backendVersion)

    raise Exception("unkown backend: %s"% backendName)
