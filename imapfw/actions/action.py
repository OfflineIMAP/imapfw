
from .devel import Devel
from .examine import Examine
from .noop import Noop
from .syncaccounts import SyncAccounts
from .testrascal import TestRascal
from .unittests import UnitTests


Actions = {
    'devel': Devel,
    'examine': Examine,
    'noop': Noop,
    'syncAccounts': SyncAccounts,
    'testRascal': TestRascal,
    'unitTests': UnitTests,
}


def Action(actionName):
    try:
        return Actions[actionName]()
    except KeyError:
        raise Exception("unkown action: %s"% actionName)
