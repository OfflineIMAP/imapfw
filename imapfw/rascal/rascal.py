
import imp
from sys import exc_info

from ..api import controllers, types


def _noop(*args):
    pass



class RascalError(Exception): pass


class RascalMind(object):
    """Low-level rascal.

    Access the spirit of the rascal (the user Python file) into a more concrete
    thing (a Python module) so we can read his minds.

    This is where the Inversion of Control happen: we give to the rascal the
    illusion he's living a real life while we keep full control of him."""

    def __init__(self):
        self._rascal = {} # The module.

    def getClass(self, name, bases):
        """Must be both re-entrant & thread-safe."""

        supportedTypes = [repr(x) for x in bases]

        # We only "read" the ressource, we're fine.
        for literal in dir(self._rascal):
            if literal != name:
                continue
            try:
                # We only "read" the ressource, we're fine.
                cls = getattr(self._rascal, literal)
                for base in bases:
                    if issubclass(cls, base):
                        return cls
            except TypeError: # getattr
                raise RascalError("'%s' does not have a supported type '%s'"%
                    (name, supportedTypes)).with_traceback(exc_info()[2])
        raise RascalError("the rascal has no class '%s' based on '%s'"%
            (name, supportedTypes)).with_traceback(exc_info()[2])

    def getFunc(self, name):
        hook = self.getLiteral(name)
        if hook is None:
            hook = _noop
        return hook

    def getLiteral(self, name):
        for literal in dir(self._rascal):
            if literal == name:
                return getattr(self._rascal, name)
        raise RascalError("the rascal does not have the literal '%s'", name)

    def load(self, path):
        rascal_mod = imp.new_module('rascal')
        rascal_mod.__file__ = path
        with open(path) as rascal_file:
            exec(compile(rascal_file.read(), path, 'exec'), rascal_mod.__dict__)
        self._rascal = rascal_mod


class HealthyRascal(object):
    """Proxy the RascalMind to allow turning it thread-safe."""

    def __init__(self):
        self._rascal = RascalMind()
        self._lock = None

    def call(self, name, *args, **kwargs):
        """How to use the RascalMind.

        Using __getattr__ and return the method would not lock the real code but
        only the "return the correct method"."""

        if self._lock is not None:
            self._lock.acquire()
        # Get the results here to actually lock the underlying code.
        values = getattr(self._rascal, name)(*args, **kwargs)
        if self._lock is not None:
            self._lock.release()
        return values

    def setLock(self, lock):
        self._lock = lock


class Rascal(object):
    """The rascal to talk with.

    It must be made thread-safe before concurrency gets used. Then, this object
    can be used whithout having to care about concurrency issues."""

    def __init__(self):
        self._rascal = HealthyRascal()

    def _getMainConf(self):
        return self._rascal.call('getLiteral', 'MainConf')

    def _getMainConfValue(self, path):
        def getItem(dictTree, pathList):
            if len(pathList) > 0:
                if isinstance(dictTree, dict):
                    newDict = dictTree.get(pathList.pop(0))
                    return getItem(newDict, pathList)
                else:
                    raise KeyError('invalid path')
            return dictTree

        mainConf = self._getMainConf()
        pathList = path.split('.')
        return getItem(mainConf, pathList)

    def configure(self, ui):
        configure = self._rascal.call('getFunc', 'configure')
        configure(ui)

    def getTypeClass(self, typeName):
        typeTypes = [
            types.Maildir,
            types.Imap,
            ]
        return self._rascal.call('getClass', typeName, typeTypes)

    def getAccountClass(self, name):
        cls_account = self._rascal.call('getClass', name, [types.Account])
        ## We want the remote on the left side; redress if necessary.
        #if not cls_account.left.isRemote and cls_account.right.isRemote:
            #cls_account.left, cls_account.right = (cls_account.right,
                #cls_account.left)
        return cls_account

    def getConcurrencyBackendName(self):
        return self._getMainConfValue('concurrency_backend')

    def getExceptionHook(self):
        return self._rascal.call('getFunc', 'exceptionHook')

    def getInitController(self):
        cls = self._rascal.call('getClass', [controllers.Init])
        if cls is None:
            cls = controllers.Init
        return cls

    def getMaxConnections(self, accountName):
        def getValue(repository):
            try:
                return int(repository.conf.get('max_connections'))
            except AttributeError:
                return 999
        cls_account = self.getAccountClass(accountName)
        max_sync = min(getValue(cls_account.left),
            getValue(cls_account.right))
        return max_sync

    def getMaxSyncAccounts(self):
        return int(self._getMainConfValue('max_sync_accounts'))

    def getPostHook(self):
        return self._rascal.call('getFunc', 'postHook')

    def getPreHook(self):
        return self._rascal.call('getFunc', 'preHook')

    def getTestClass(self, name):
        # Import here to avoid dependency loop: any action might import this
        # module.
        from ..api import actions
        return self._rascal.call('getClass', name, [actions.UnitTests])

    def load(self, path):
        self._rascal.call('load', path)

    def setLock(self, lock):
        self._rascal.setLock(lock)
