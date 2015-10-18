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
