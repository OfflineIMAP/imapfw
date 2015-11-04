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

from imapfw import runtime
from imapfw.types.repository import loadRepository

from .folder import Folders


class AccountInternalInterface(object):
    def fw_getLeft(self):   raise NotImplementedError
    def fw_getRight(self):  raise NotImplementedError


class AccountInterface(object):
    def getClassName(self): raise NotImplementedError
    def syncFolders(self):  raise NotImplementedError


class Account(AccountInterface, AccountInternalInterface):
    """The Account base class.

    The namespace `fw_` is reserved for the framework internals."""

    left = None
    right = None

    def fw_getSide(self, side: str) -> 'complete repository':
        if side == 'left':
            return self.fw_getLeft()
        if side == 'right':
            return self.fw_getRight()
        assert side in ['left', 'right']

    def fw_getLeft(self):
        return loadRepository(self.left)

    def fw_getRight(self):
        return loadRepository(self.right)

    def getClassName(self) -> str:
        return self.__class__.__name__

    def init(self):
        """Override this method to make initialization in the rascal."""

        pass

    def syncFolders(self, folders: Folders) -> Folders:
        return folders


def loadAccount(obj: 'account class or str name') -> 'initialized Account':

    if isinstance(obj, str):
        obj = runtime.rascal.get(obj, [Account, dict])

    try:
        if issubclass(obj, Account):
            cls_account = obj
        else:
            raise TypeError()

    except TypeError:
        try:
            if not issubclass(obj, dict):
                raise TypeError()

            else:
                cls_account = type(obj.get('name'), obj.get('type'), {})

                # Attach attributes.
                for name in ['left', 'right', 'conf']:
                    setattr(cls_account, name, obj.get(name))
        except TypeError:
            raise TypeError("'%s' for a account is not supported"% type(obj))

    account = cls_account()
    account.init()
    return account
