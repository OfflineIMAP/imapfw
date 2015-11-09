
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
        from imapfw.testing.concurrency import TestConcurrency
        from imapfw.testing.rascal import TestRascal
        from imapfw.testing.folder import TestFolder
        from imapfw.testing.maildir import TestMaildirDriver
        from imapfw.testing.edmp import TestEDMP
        from imapfw.testing.types import TestTypeAccount, TestTypeRepository
        from imapfw.testing.architect import TestArchitect, TestDriverArchitect
        from imapfw.testing.architect import TestDriversArchitect
        from imapfw.testing.architect import TestEngineArchitect

        self._suite.addTest(unittest.makeSuite(TestConcurrency))
        self._suite.addTest(unittest.makeSuite(TestRascal))
        self._suite.addTest(unittest.makeSuite(TestFolder))
        self._suite.addTest(unittest.makeSuite(TestMaildirDriver))
        self._suite.addTest(unittest.makeSuite(TestEDMP))
        self._suite.addTest(unittest.makeSuite(TestTypeAccount))
        self._suite.addTest(unittest.makeSuite(TestTypeRepository))
        self._suite.addTest(unittest.makeSuite(TestArchitect))
        self._suite.addTest(unittest.makeSuite(TestDriverArchitect))
        self._suite.addTest(unittest.makeSuite(TestDriversArchitect))
        self._suite.addTest(unittest.makeSuite(TestEngineArchitect))

    def run(self):
        import unittest

        runner = unittest.TextTestRunner(verbosity=2)
        testResult = runner.run(self._suite)
        if testResult.wasSuccessful():
            self._exitCode = len(testResult.failures)
