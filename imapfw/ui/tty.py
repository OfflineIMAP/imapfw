
import logging
import logging.config


logging_config = {
    'version': 1,
    'formatters': {
        'default': {
            'class': 'logging.Formatter',
            'format': '%(message}',
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
    def critical(self, *args): raise NotImplementedError
    def debug(self, *args): raise NotImplementedError
    def debugC(self, category, *args): raise NotImplementedError
    def error(self, *args): raise NotImplementedError
    def exception(self, *args): raise NotImplementedError
    def format(self, *args): raise NotImplementedError
    def info(self, *args): raise NotImplementedError
    def infoL(self, level, *args): raise NotImplementedError
    def setInfoLevel(self, level): raise NotImplementedError
    def warn(self, *args): raise NotImplementedError


class UIbackendInterface(object):
    def __init__(self, lock): raise NotImplementedError
    def configure(self, config=logging_config): raise NotImplementedError
    def enableDebugCategories(self, categories): raise NotImplementedError
    def setCurrentWorkerNameFunction(self, func): raise NotImplementedError


class TTY(UIinterface, UIbackendInterface):
    def __init__(self, lock):
        self._lock = lock

        self._config = logging.config
        self._logger = None
        self._backend = logging
        self._currentWorkerName = lambda *args: ''
        self._debugCategories = {
            'emitters': False,
            'drivers': False,
            'controllers': False,
            'workers': False,
            }
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
        if self._debugCategories[category] is True:
            self._safeLog('debug', "%s: %s",
                self._currentWorkerName(), self.format(*args))

    def enableDebugCategories(self, categories):
        for category in categories:
            self._debugCategories[category] = True

    def error(self, *args):
        self._safeLog('error', *args)

    def exception(self, *args):
        self._safeLog('exception', *args)

    def format(self, *args):
        format_args = args[1:]
        return args[0].format(*format_args)

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
