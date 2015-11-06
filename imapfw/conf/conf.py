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

import logging

from imapfw.runtime import set_module
from imapfw.concurrency import Concurrency
from imapfw.rascal import Rascal
from imapfw.ui.tty import TTY

from .clioptions import CLIOptions


class ImapfwConfig(object):
    def __init__(self):
        self._cli = None
        self._concurrency = None
        self._rascal = None
        self._ui = None

    def getAction(self):
        return self._cli.get('action')

    def getActionOptions(self):
        actionName = self.getAction()
        mapping = {
            'devel': [],
            'examine': ['repositories'],
            'noop': [],
            'syncAccounts': ['accounts', 'engine'],
            'testRascal': [],
            'unitTests': [],
        }
        options = {}

        for option in mapping[actionName]:
            options[option] = self._cli.get(option)
        options['action'] = actionName
        return options

    def getConcurrency(self):
        return self._concurrency

    def getLogger(self):
        return logging

    def getRascal(self):
        return self._rascal

    def getUI(self):
        return self._ui

    def listActions(self):
        return self._cli.get('listActions')

    def setupConcurrency(self):
        self._concurrency = Concurrency(self._cli.get('concurrency'))
        set_module('concurrency', self._concurrency) # Export concurrency module.

    def loadRascal(self):
        rascalFile = self._cli.get('rascalfile')
        if rascalFile is not None:
            self._rascal = Rascal()
            self._rascal.load(rascalFile)
        set_module('rascal', self._rascal) # Export the rascal.

    def parseCLI(self):
        if self._cli is None:
            self._cli = CLIOptions()
            self._cli.parse()

    def setupUI(self):
        ui = TTY(self._concurrency.createLock())
        ui.configure()

        # Let ui prefix log lines with the worker name.
        ui.setCurrentWorkerNameFunction(self._concurrency.getCurrentWorkerNameFunction())
        # Apply CLI options.
        ui.enableDebugCategories(self._cli.get('debug'))
        ui.setInfoLevel(self._cli.get('info'))

        self._ui = ui
        set_module('ui', ui) # Export ui module.
