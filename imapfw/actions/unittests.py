
from .interface import ActionInterface


class UnitTests(ActionInterface):
    """Run all the unit tests."""

    honorHooks = False
    requireRascal = False

    def __init__(self):
        self._suite = None
        self._exitCode = 1

    def exception(self, e):
        raise

    def getExitCode(self):
        return self._exitCode

    def init(self, actionOptions):
        import unittest

        self._suite = unittest.TestSuite()

        # Load all available unit tests.
        from imapfw.testing.concurrency import TestMultiProcessing
        from imapfw.testing.rascal import TestRascal
        from imapfw.testing.folder import TestFolder
        from imapfw.testing.maildir import TestMaildirDriver

        self._suite.addTest(unittest.makeSuite(TestMultiProcessing))
        self._suite.addTest(unittest.makeSuite(TestRascal))
        self._suite.addTest(unittest.makeSuite(TestFolder))
        self._suite.addTest(unittest.makeSuite(TestMaildirDriver))

    def run(self):
        import unittest

        runner = unittest.TextTestRunner(verbosity=2)
        testResult = runner.run(self._suite)
        if testResult.wasSuccessful():
            self._exitCode = 0
