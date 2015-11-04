"""

The public API.

Import the objects made public from the real objects defined in their
uncorrelated path. This allows more fine-grained control of what is made public
and how to structure the underlying code.

"""

__all__ = [
    'folder',
    'Account',
    'Imap',
    'Maildir',
    'Repository',
]

from imapfw.types import folder
from imapfw.types.account import Account
from imapfw.types.imap import Imap
from imapfw.types.maildir import Maildir
from imapfw.types.repository import Repository
