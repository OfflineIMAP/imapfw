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

import logging
import logging.config

from imapfw.constants import DEBUG_CATEGORIES, DEFAULT_DEBUG_CATEGORIES

logging_config = {
    'version': 1,
    'formatters': {
        'default': {
            'class': 'logging.Formatter',
            'format': '%(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
        },
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['console'],
    },
}




class UIinterface(object):
    def critical(self):     raise NotImplementedError
    def debug(self):        raise NotImplementedError
    def debugC(self):       raise NotImplementedError
    def error(self):        raise NotImplementedError
    def exception(self):    raise NotImplementedError
    def format(self):       raise NotImplementedError
    def info(self):         raise NotImplementedError
    def infoL(self):        raise NotImplementedError
    def setInfoLevel(self): raise NotImplementedError
    def warn(self):         raise NotImplementedError


class UIbackendInterface(object):
    def configure(self):                    raise NotImplementedError
    def enableDebugCategories(self):        raise NotImplementedError
    def setCurrentWorkerNameFunction(self): raise NotImplementedError


class TTY(UIinterface, UIbackendInterface):
    def __init__(self, lock):
        self._lock = lock

        self._config = logging.config
        self._logger = None
        self._backend = logging
        self._currentWorkerName = lambda *args: ''
        self._debugCategories = DEBUG_CATEGORIES
        self._infoLevel = None

    def _safeLog(self, name, *args):
        self._lock.acquire()
        getattr(self._logger, name)(*args)
        self._lock.release()

    def configure(self, config=logging_config):
        self._backend.config.dictConfig(config)
        self._logger = self._backend.getLogger('setup')

    def critical(self, *args):
        self._safeLog('critical', *args)

    def debug(self, *args):
        self._safeLog('debug', *args)

    def debugC(self, category, *args):
        if self._debugCategories.get(category) is True:
            self._safeLog('debug', "%s %s [%s]",
                self._currentWorkerName(),
                self.format(*args),
                category,
                )

    def enableDebugCategories(self, categories):
        if 'all' in categories:
            categories = DEFAULT_DEBUG_CATEGORIES
        for category in categories:
            self._debugCategories[category] = True

    def error(self, *args):
        self._safeLog('error', *args)

    def exception(self, *args):
        self._safeLog('exception', *args)

    def format(self, *args):
        format_args = args[1:]
        try:
            return args[0].format(*format_args)
        except (IndexError, KeyError):
            return args[0] % args[1:]


    def info(self, *args):
        self._safeLog('info', *args)

    def infoL(self, level, *args):
        if level <= self._infoLevel:
            self.info(*args)

    def setCurrentWorkerNameFunction(self, func):
        self._currentWorkerName = func

    def setInfoLevel(self, level):
        self._infoLevel = level

    def warn(self, *args):
        self._safeLog('warn', *args)
