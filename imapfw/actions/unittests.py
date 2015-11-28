# The MIT License (MIT).
# Copyright (c) 2015, Nicolas Sebrecht & contributors.

from imapfw.interface import implements

from .interface import ActionInterface

# Annotations.
from imapfw.annotation import ExceptionClass, Dict


@implements(ActionInterface)
class UnitTests(object):
    """Run all the unit tests."""

    honorHooks = False
    requireRascal = False

    def __init__(self):
        self._suite = None
        self._exitCode = 1

    def exception(self, e: ExceptionClass) -> None:
        raise

    def getExitCode(self) -> int:
        return self._exitCode

    def init(self, options: Dict) -> None:
        import unittest

        self._suite = unittest.TestSuite()

        # Load all available unit tests.
        from imapfw.testing.concurrency import TestConcurrency
        from imapfw.testing.rascal import TestRascal
        from imapfw.testing.folder import TestFolder
        from imapfw.testing.message import TestMessage, TestMessages
        from imapfw.testing.maildir import TestMaildirDriver
        from imapfw.testing.edmp import TestEDMP
        from imapfw.testing.types import TestTypeAccount, TestTypeRepository
        from imapfw.testing.architect import TestArchitect, TestDriverArchitect
        from imapfw.testing.architect import TestDriversArchitect
        from imapfw.testing.architect import TestEngineArchitect

        self._suite.addTest(unittest.makeSuite(TestConcurrency))
        self._suite.addTest(unittest.makeSuite(TestRascal))
        self._suite.addTest(unittest.makeSuite(TestFolder))
        self._suite.addTest(unittest.makeSuite(TestMessage))
        self._suite.addTest(unittest.makeSuite(TestMessages))
        self._suite.addTest(unittest.makeSuite(TestMaildirDriver))
        self._suite.addTest(unittest.makeSuite(TestEDMP))
        self._suite.addTest(unittest.makeSuite(TestTypeAccount))
        self._suite.addTest(unittest.makeSuite(TestTypeRepository))
        self._suite.addTest(unittest.makeSuite(TestArchitect))
        self._suite.addTest(unittest.makeSuite(TestDriverArchitect))
        self._suite.addTest(unittest.makeSuite(TestDriversArchitect))
        self._suite.addTest(unittest.makeSuite(TestEngineArchitect))

    def run(self) -> None:
        import unittest

        runner = unittest.TextTestRunner(verbosity=2)
        testResult = runner.run(self._suite)
        if testResult.wasSuccessful():
            self._exitCode = len(testResult.failures)
