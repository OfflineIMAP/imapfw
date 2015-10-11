
"""

Imap types and derivatives.

"""

from .repository import RepositoryBase


class Imap(RepositoryBase):
    def __init__(self, conf):
        self._conf = conf
