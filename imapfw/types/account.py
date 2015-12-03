# The MIT License (MIT).
# Copyright (c) 2015, Nicolas Sebrecht & contributors.

from typing import TypeVar, Union

from imapfw import runtime
from imapfw.types.repository import loadRepository

from .folder import Folders

# Annotations.
from imapfw.types.repository import Repository


AccountClass = TypeVar('Account based class')


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

    def fw_getSide(self, side: str) -> Repository:
        if side == 'left':
            return self.fw_getLeft()
        if side == 'right':
            return self.fw_getRight()
        assert side in ['left', 'right']

    def fw_getLeft(self) -> Repository:
        return loadRepository(self.left)

    def fw_getRight(self) -> Repository:
        return loadRepository(self.right)

    def getClassName(self) -> str:
        return self.__class__.__name__

    def init(self) -> None:
        """Override this method to make initialization in the rascal."""

        pass

    def syncFolders(self, folders: Folders) -> Folders:
        return folders


def loadAccount(obj: Union[AccountClass, str]) -> Account:

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
            raise TypeError("'%s' for a account is not supported"% repr(obj))

    account = cls_account()
    account.init()
    return account
