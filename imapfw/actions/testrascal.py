# The MIT License (MIT).
# Copyright (c) 2015, Nicolas Sebrecht & contributors.


from imapfw import runtime
from imapfw.interface import implements

from .interface import ActionInterface

# Annotations.
from imapfw.annotation import ExceptionClass, Dict


@implements(ActionInterface)
class TestRascal(object):
    """Test the rascal."""

    honorHooks = False
    requireRascal = True

    def __init__(self):
        self._suite = None
        self._exitCode = -1

    def _setExitCode(self, exitCode):
        if exitCode > self._exitCode:
            self._exitCode = exitCode

    def exception(self, e: ExceptionClass) -> None:
        # This should not happen since all exceptions are handled at lower level.
        raise NotImplementedError

    def getExitCode(self) -> int:
        return self._exitCode

    def init(self, options: Dict) -> None:
        pass

    def run(self) -> None:
        import unittest

        from imapfw.types.account import Account
        from imapfw.testing.testrascal import TestRascalAccount

        suite = unittest.TestSuite()

        for def_account in runtime.rascal.getAll([Account]):
            newTest = type(def_account.__name__, (TestRascalAccount,), {})
            newTest.DEF_ACCOUNT = def_account
            suite.addTest(unittest.makeSuite(newTest))

        runner = unittest.TextTestRunner(verbosity=2, failfast=True)
        testResult = runner.run(suite)
        self._setExitCode(len(testResult.failures))

        if testResult.wasSuccessful():
            print("TODO: run tests for the repositories and drivers.")
