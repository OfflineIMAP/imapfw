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
