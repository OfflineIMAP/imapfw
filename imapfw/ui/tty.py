# The MIT License (MIT).
# Copyright (c) 2015-2016, Nicolas Sebrecht & contributors.

import logging
import logging.config

from imapfw.constants import DEBUG_CATEGORIES, DEBUG_ALL_CATEGORIES

# Annotations.
from imapfw.annotation import List, Function

logging_config = {
    'version': 1,
    'formatters': {
        'brief': {
            'class': 'logging.Formatter',
            'format': '%(message)s',
        },
        'default': {
            'class': 'logging.Formatter',
            'format': '%(levelname)-8s: %(message)s',
        },
        'verbose': {
            'class': 'logging.Formatter',
            'format': '%(levelname)-8s %(module)s: %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
    },
    'loggers': {
        'debug': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
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

        self._logger = None
        self._backend = logging
        self._currentWorkerName = lambda *args: ''
        self._debugCategories = DEBUG_CATEGORIES
        self._infoLevel = None

    def _safeLog(self, name: str, *args) -> None:
        self._lock.acquire()
        getattr(self._logger, name)(*args)
        self._lock.release()

    def configure(self, config: dict=logging_config) -> None:
        self._backend.config.dictConfig(config)
        self._logger = self._backend.getLogger('debug')

    def critical(self, *args) -> None:
        self._safeLog('critical', *args)

    def debug(self, *args) -> None:
        self._safeLog('debug', *args)

    def debugC(self, category: str, *args) -> None:
        if self._debugCategories.get(category) is True:
            self._safeLog('debug', "%s %s [%s]",
                self._currentWorkerName(),
                self.format(*args),
                category,
                )

    def enableDebugCategories(self, categories: List[str]) -> None:
        if 'all' in categories:
            categories = DEBUG_ALL_CATEGORIES
        for category in categories:
            self._debugCategories[category] = True

    def error(self, *args) -> None:
        self._safeLog('error', *args)

    def exception(self, *args) -> None:
        self._safeLog('exception', *args)

    def format(self, *args):
        format_args = args[1:]
        try:
            return args[0].format(*format_args)
        except (IndexError, KeyError):
            return args[0] % args[1:]


    def info(self, *args) -> None:
        self._safeLog('info', *args)

    def infoL(self, level, *args) -> None:
        if level <= self._infoLevel:
            self.info(*args)

    def setCurrentWorkerNameFunction(self, func: Function) -> None:
        self._currentWorkerName = func

    def setInfoLevel(self, level: int) -> None:
        self._infoLevel = level

    def warn(self, *args) -> None:
        self._safeLog('warn', *args)
