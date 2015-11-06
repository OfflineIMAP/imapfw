# The MIT License (MIT)
#
# Copyright (c) 2015, Nicolas Sebrecht & contributors
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


from imapfw import runtime

from .interface import ActionInterface


class TestRascal(ActionInterface):
    """Test the rascal."""

    honorHooks = False
    requireRascal = True

    def __init__(self):
        self._suite = None
        self._exitCode = -1

    def _setExitCode(self, exitCode):
        if exitCode > self._exitCode:
            self._exitCode = exitCode

    def exception(self, e):
        # This should not happen since all exceptions are handled at lower level.
        raise NotImplementedError

    def getExitCode(self):
        return self._exitCode

    def init(self, options):
        pass

    def run(self):
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
