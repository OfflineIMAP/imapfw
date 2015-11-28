# The MIT License (MIT).
# Copyright (c) 2015, Nicolas Sebrecht & contributors.

from .devel import Devel
from .examine import Examine
from .noop import Noop
from .shell import ShellAction
from .syncaccounts import SyncAccounts
from .testrascal import TestRascal
from .unittests import UnitTests


Actions = {
    'devel': Devel,
    'examine': Examine,
    'noop': Noop,
    'shell': ShellAction,
    'syncAccounts': SyncAccounts,
    'testRascal': TestRascal,
    'unitTests': UnitTests,
}


def Action(actionName :str):
    try:
        return Actions[actionName]()
    except KeyError:
        raise Exception("unkown action: %s"% actionName)
