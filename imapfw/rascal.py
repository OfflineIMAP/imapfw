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

import imp #TODO: use library importlib instead of deprecated imp.

from imapfw.api import types

# Annotations.
from typing import List, TypeVar


Function = TypeVar('Function')
Class = TypeVar('Class')


class Rascal(object):
    """The Rascal.

    Turn the rascal (the user Python file given at CLI) into a more concrete
    thing (a Python module).

    This is where the Inversion of Control happen: we give to the rascal the
    illusion he's living a real life while we keep full control of him."""

    def __init__(self):
        self._rascal = {} # The module.
        # Cached literals.
        self._mainConf = None

    def _isDict(self, obj: object) -> bool:
        try:
            return type(obj) == dict
        except:
            raise TypeError("'%s' must be a dictionnary, got '%s'"%
                (obj.__name__, type(obj)))

    def _getHook(self, name: str) -> Function:
        try:
            return self.getFunction(name)
        except:
            return lambda *args: None

    def _getLiteral(self, name: str) -> type:
        return getattr(self._rascal, name)

    def get(self, name: str, expectedTypes: List[Class]):
        cls = self._getLiteral(name)

        for expectedType in expectedTypes:
            if issubclass(cls, expectedType):
                return cls

        raise TypeError("class '%s' is not a sub-class of '%s'"%
            (name, expectedTypes))

    def getAll(self, targetTypes: List[Class]) -> List[Class]:
        classes = []
        for literal in dir(self._rascal):
            if literal.startswith('_'):
                continue
            try:
                classes.append(self.get(literal, targetTypes))
            except TypeError:
                pass
        return classes

    def getExceptionHook(self) -> Function:
        return self._getHook('exceptionHook')

    def getFunction(self, name: str) -> Function:
        func = self._getLiteral(name)
        if not callable(func):
            raise TypeError("function expected for '%s'"% name)
        return func

    def getMaxConnections(self, accountName: str) -> int:
        def getValue(repository):
            try:
                return int(repository.conf.get('max_connections'))
            except AttributeError:
                return 999

        account = self.get(accountName, [types.Account])
        max_sync = min(getValue(account.left),
            getValue(account.right))
        return max_sync

    def getMaxSyncAccounts(self) -> int:
        return int(self._mainConf.get('max_sync_accounts'))

    def getPostHook(self) -> Function:
        return self._getHook('postHook')

    def getPreHook(self) -> Function:
        return self._getHook('preHook')

    def getSettings(self, name: str) -> dict:
        literal = getattr(self._rascal, name)
        if not isinstance(literal, dict):
            raise TypeError("expected dict for '%s', got '%s'"%
                (name, type(literal)))
        return literal

    def load(self, path: str) -> None:
        # Create empty module.
        rascal_mod = imp.new_module('rascal')
        rascal_mod.__file__ = path

        with open(path) as rascal_file:
            exec(compile(
                rascal_file.read(), path, 'exec'), rascal_mod.__dict__)
        self._rascal = rascal_mod

        self._mainConf = self.getSettings('MainConf')

        # Turn accounts definitions from MainConf into global of rascal
        # literals.
        if 'accounts' in self._mainConf:
            for accountDict in self._mainConf.get('accounts'):
                setattr(self._rascal, accountDict.get('name'), accountDict)
