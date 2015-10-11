
import imp

from ..api import types


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

    def _isDict(self, obj):
        if not isinstance(obj, dict):
            raise TypeError("'%s' must be a dictionnary, got '%s'"%
                obj.__name__, type(obj))
    def _getHook(self, name):
        try:
            return self.getFunction(name)
        except:
            return lambda *args: None

    def _getLiteral(self, name):
        return getattr(self._rascal, name)

    def get(self, name, expectedTypes, defaultConstructor=None):
        literal = self._getLiteral(name)

        for expectedType in expectedTypes:
            if issubclass(literal, expectedType):
                return literal()

        if defaultConstructor is not None:
            try:
                self._isDict(literal)
                return defaultConstructor(literal)
            except:
                pass

        raise TypeError("literal '%s' has unexpected type '%s'"%
            (name, type(literal)))

    def getExceptionHook(self):
        return self._getHook('exceptionHook')

    def getFunction(self, name):
        func = self._getLiteral(name)
        if not callable(func):
            raise TypeError("function expected for '%s'"% name)
        return func

    def getMaxConnections(self, accountName):
        def getValue(repository):
            try:
                return int(repository.conf.get('max_connections'))
            except AttributeError:
                return 999

        account = self.get(accountName, [types.Account])
        max_sync = min(getValue(account.left),
            getValue(account.right))
        return max_sync

    def getMaxSyncAccounts(self):
        return int(self._mainConf.get('max_sync_accounts'))

    def getPostHook(self):
        return self._getHook('postHook')

    def getPreHook(self):
        return self._getHook('preHook')

    def getSettings(self, name):
        literal = getattr(self._rascal, name)
        if not isinstance(literal, dict):
            raise TypeError("expected dict for '%s', got '%s'"%
                (name, type(literal)))
        return literal

    def load(self, path):
        # Create empty module.
        rascal_mod = imp.new_module('rascal')
        rascal_mod.__file__ = path

        with open(path) as rascal_file:
            exec(compile(rascal_file.read(), path, 'exec'), rascal_mod.__dict__)
        self._rascal = rascal_mod

        self._mainConf = self.getSettings('MainConf')
