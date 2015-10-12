
from .syncaccounts import SyncAccounts
from .tests import UnitTests
from .noop import Noop
from .dev import Devel


Actions = {
    'devel': Devel,
    'noop': Noop,
    'unitTests': UnitTests,
    'syncAccounts': SyncAccounts,
}


def Action(actionName):
    try:
        return Actions[actionName]()
    except KeyError:
        raise Exception("unkown action: %s"% actionName)
