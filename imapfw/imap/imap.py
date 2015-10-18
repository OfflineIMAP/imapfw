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

"""

Backends that implement IMAP protocol.

Don't expose IMAP states and other low-level IMAP issues. The Imap driver
doesn't care at all.

"""

from importlib import import_module

#from .imapc.interface import IMAPcInterface


# Exceptions.
class ImapInternalError(Exception): pass
class ImapTemporaryError(ImapInternalError): pass
class ImapAbortError(ImapInternalError): pass


#TODO: move to imapc/interface.py
class IMAPcInterface(object):
    def configure(self, ui): raise NotImplementedError
    def connect(self, host, port): raise NotImplementedError
    def logout(self): raise NotImplementedError


class IMAPlib2_skater(IMAPcInterface):
    """Allows to use imaplib2 (or imaplib3) with the API of IMAPc."""

    def __init__(self, imaplib2):
        self._imaplib2 = imaplib2 # Might be imaplib3!
        self._ui = None
        self._imap = None

    def configure(self, ui):
        self._ui = ui

    def connect(self, host, port):
        #TODO: expose more like debug level.
        try:
            self._imap = self._imaplib2.IMAP4(host, port, debug=3, timeout=2)
            return True
        finally:
            res = self._imap.logout()
            self._ui.debug("logout %s", res)

    def logout(self):
        self._imap.logout()



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

    # imaplib2
    if backendName == 'imaplib2':
        if version is None:
            version = '2_50'
        else:
            version = '_'.join(version.split('.'))

        mod_imaplib2 = import_module(".imap.imaplib2.imaplib2_%s"% version, 'imapfw')
        return IMAPlib2_skater(mod_imaplib2)

    # imaplib3
    if backendName == 'imaplib3':
        from .imaplib3 import imaplib3
        return IMAPlib2_skater(imaplib3)

    raise Exception("unkown backend: %s"% backendName)
