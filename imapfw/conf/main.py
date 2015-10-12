# Copyright (C) 2015 Nicolas Sebreht & contributors
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA


import logging

from .clioptions import CLIOptions

from ..concurrency.concurrency import Concurrency
from ..rascal import Rascal
from ..ui.tty import TTY


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
            'noop': [],
            'unitTests': [],
            'syncAccounts': ['accounts', 'engine'],
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

    def loadRascal(self):
        rascalFile = self._cli.get('rascalfile')
        if rascalFile is not None:
            self._rascal = Rascal()
            self._rascal.load(rascalFile)

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
