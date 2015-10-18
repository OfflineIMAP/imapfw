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


class Devel(ActionInterface):
    """For development purpose only."""

    honorHooks = False
    requireRascal = True

    def __init__(self):
        self._exitCode = 0

        self.ui = runtime.ui
        self.concurrency = runtime.concurrency
        self.rascal = runtime.rascal
        self._options = {}

    def exception(self, e):
        self._exitCode = 3

    def getExitCode(self):
        return self._exitCode

    def init(self, options):
        self._options = options

    def run(self):
        self.ui.infoL(1, 'running devel action')

        from ..imap.imap import Imap

        imap = Imap('imaplib2-2.50')
        imap.configure(self.ui)
        imap.connect('127.0.0.1', 10143)
        imap.logout()
