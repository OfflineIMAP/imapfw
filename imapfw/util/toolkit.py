

import os


def runHook(f, *args):
    # TODO: run f() in a timeout thread.
    return f(*args)


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
