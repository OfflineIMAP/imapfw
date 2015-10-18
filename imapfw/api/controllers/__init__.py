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
    'Filter',
    'NameTrans',
    'Transcoder',
]

from ...controllers.controller import Controller
from ...controllers.duplicate import Duplicate
from ...controllers.examine import ExamineController as Examine
from ...controllers.filter import Filter
from ...controllers.nametrans import NameTrans
from ...controllers.transcoder import Transcoder
