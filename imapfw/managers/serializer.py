

class SerializerInterface(object):
    """Allow sending serialized objects between workers."""

    def dump(self):                 raise NotImplementedError
    def load(self, serialized):     raise NotImplementedError
