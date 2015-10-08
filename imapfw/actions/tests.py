
from .interface import ActionInterface


class UnitTests(ActionInterface):
    """Run all the unit tests."""

    def __init__(self):
        self._ui = None
        self._suite = None

    def exception(self, e):
        raise

    def getExitCode(self):
        return 0

    def initialize(self, ui, rascal, actionOptions):
        import unittest

        self._ui = ui
        self._suite = unittest.TestSuite()

        # Load all available unit tests.
        from ..testing.concurrency import TestMultiProcessing
        from ..testing.rascal import TestRascal

        self._suite.addTest(unittest.makeSuite(TestMultiProcessing))
        self._suite.addTest(unittest.makeSuite(TestRascal))

    def run(self):
        import unittest

        #self._ui.info("Total: %i test cases"% len(self._testCases))
        #for testCase in self._testCases:
            #self._ui.info("\n>>> Running tests of %s"% testCase.__name__)
            #runner = unittest.TextTestRunner(verbosity=2)
            #runner.run(unittest.defaultTestLoader.loadTestsFromTestCase(testCase))

        runner = unittest.TextTestRunner(verbosity=2)
        runner.run(self._suite)

