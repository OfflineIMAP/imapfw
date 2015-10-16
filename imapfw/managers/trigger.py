

class Trigger(object):
    def __init__(self, name, result=None):
        self._name = name
        self._result = result

        self._cls_error = None
        self._message = None

    def getName(self):
        return self._name

    def getResult(self):
        if self._cls_error is not None:
            raise self._cls_error(self._message)
        return self._result

    def setError(self, cls_error, message):
        self._cls_error = cls_error
        self._message = message
