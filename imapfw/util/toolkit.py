

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
    hook = Hook()
    if hookName == 'preHook':
        args += (hook,)
    thread = Thread(name=hookName, target=hookFunc, args=args)
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

def expandpath(path):
    xtrans = [os.path.expanduser, os.path.expandvars]
    return xTrans(path, xtrans)
