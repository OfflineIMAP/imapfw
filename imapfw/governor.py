

class Governor(object):
    def __init__(self):
        self._emitters = []

    def deregister(self, emitter):
        self._emitters.remove(emitter)

    def register(self, emitter):
        self._emitters.append(emitter)

    # What a POOR name!
    def wait(self):
        for emitter in self._emitters:
            emitter.honor_pending()
