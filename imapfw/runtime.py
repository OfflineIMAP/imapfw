# The MIT License (MIT).
# Copyright (c) 2015, Nicolas Sebrecht & contributors.

"""

The module to handle modules configured at runtime.

Once modules are set, can be used like this:

    import runtime

    def whatever():
        ui = runtime.ui

Since the import is done at import time, this won't work:

    import runtime
    ui = runtime.ui # Gets None.

"""

import sys


class CacheUI(object):
    def __init__(self):
        self.number = 0
        self.cached = {}
        self.lastName = None

    def __getattr__(self, name):
        self.lastName = name
        return self.cache

    def _getNumber(self):
        self.number += 1
        return self.number

    def cache(self, *args, **kwargs):
        self.cached[self._getNumber()] = (self.lastName, args, kwargs)

    def unCache(self, ui):
        for cached in self.cached.values():
            name, args, kwargs = cached
            getattr(ui, name)(*args, **kwargs)


# Put this runtime module into _this variable so we use setattr.
_this = sys.modules.get(__name__)

ui = CacheUI() # Cache logs until true UI is set.
concurrency = None
rascal = None

def set_module(name, mod):
    if name == 'ui':
        previousUI = getattr(_this, 'ui')
        try:
            previousUI.unCache(mod)
        except AttributeError:
            pass
    setattr(_this, name, mod)
