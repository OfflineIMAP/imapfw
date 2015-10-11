
from .syncaccounts import SyncAccounts
from .tests import UnitTests
from .noop import Noop


Actions = {
    'noop': Noop,
    'unitTests': UnitTests,
    'syncAccounts': SyncAccounts,
}


def Action(actionName):
    try:
        return Actions[actionName]()
    except KeyError:
        raise Exception("unkown action: %s"% actionName)
