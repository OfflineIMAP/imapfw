"""

The public API.

Import the objects made public from the real objects defined in their
uncorrelated path. This allows more fine-grained control of what is made public
and how to structure the underlying code.

"""

__all__ = [
    'Controller',
    'Duplicate',
    'Examine',
    'FakeDriver',
    'Filter',
    'NameTrans',
    'Transcoder',
]

from imapfw.controllers.controller import Controller
from imapfw.controllers.duplicate import Duplicate
from imapfw.controllers.examine import ExamineController as Examine
from imapfw.controllers.fake import FakeDriver
from imapfw.controllers.filter import Filter
from imapfw.controllers.nametrans import NameTrans
from imapfw.controllers.transcoder import Transcoder
