
from .interface import ActionInterface


class UnitTests(ActionInterface):
    """Run all the unit tests."""

    honorHooks = False
    requireRascal = False

    def __init__(self):
        self._suite = None

    def exception(self, e):
        raise

    def getExitCode(self):
        return 0

    def init(self, actionOptions):
        import unittest

        self._suite = unittest.TestSuite()

        # Load all available unit tests.
        from ..testing.concurrency import TestMultiProcessing
        from ..testing.rascal import TestRascal
        from ..testing.syncaccounts import TestSyncAccounts
        from ..testing.folder import TestFolder
        from ..testing.maildir import TestMaildirDriver

        self._suite.addTest(unittest.makeSuite(TestMultiProcessing))
        self._suite.addTest(unittest.makeSuite(TestRascal))
        self._suite.addTest(unittest.makeSuite(TestSyncAccounts))
        self._suite.addTest(unittest.makeSuite(TestFolder))
        self._suite.addTest(unittest.makeSuite(TestMaildirDriver))

    def run(self):
        import unittest

        runner = unittest.TextTestRunner(verbosity=2)
        runner.run(self._suite)

