

import os
from threading import Thread

def runHook(hookFunc, *args):
    class Hook(object):
        def __init__(self):
            self._stop = True

        def ended(self):
            self._stop = False

        def stop(self):
            return self._stop


    hookName = hookFunc.__name__

    # Don't run hooks for action unitTests.
    if hookName == 'preHook':
        if args[0] == 'unitTests':
            return False

    hook = Hook()

    if hookName == 'preHook':
        args += (hook,)

    thread = Thread(name=hookName, target=hookFunc, args=args, daemon=True)
    thread.start()
    thread.join(10) # TODO: get timeout from rascal.

    return hook.stop()


def xTrans(thing, transforms):
    """Applies set of transformations to a thing.

    :args:
     - thing: string; if None, then no processing will take place.
     - transforms: iterable that returns transformation function
       on each turn.

    Returns transformed thing."""

    if thing == None:
        return None
    for f in transforms:
        thing = f(thing)
    return thing

def expandPath(path):
    xtrans = [os.path.expanduser, os.path.expandvars, os.path.abspath]
    return xTrans(path, xtrans)


def dictValueFromPath(dictionnary, path):
    def getItem(tmpDict, lst_path):
        if len(lst_path) > 0:
            if isinstance(tmpDict, dict):
                newDict = tmpDict.get(lst_path.pop(0))
                return getItem(newDict, lst_path)
            else:
                raise KeyError('invalid path')
        return tmpDict

    lst_path = path.split('.')
    return getItem(dictionnary, lst_path)
