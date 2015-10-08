
from .syncaccounts import SyncAccounts
from .tests import UnitTests
from .noop import Noop


Actions = {
    'noop': Noop,
    'unitTests': UnitTests,
    'syncAccounts': SyncAccounts,
}


def Action(action):
    try:
        return Actions[action]()
    except KeyError:
        raise Exception("unkown action: %s"% action)
