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
from ..rascal.rascal import Rascal
from ..ui.tty import TTY


class ImapfwConfig(object):
    def __init__(self):
        self._cli = None
        self._uiInst = None
        self._localevalInst = None
        self._rascal = None

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

    def getLogger(self):
        return logging

    def getRascal(self):
        return self._rascal

    def getUIinst(self):
        return self._uiInst

    def listActions(self):
        return self._cli.get('listActions')

    def loadRascal(self):
        self._rascal = Rascal()
        self._rascal.load(self._cli.get('rascalfile'))

    def parseCLI(self):
        if self._cli is None:
            self._cli = CLIOptions()
            self._cli.parse()

    def printRascal(self):
        return self._cli.get('rascaldefault')

    def setupUI(self):
        ui = TTY()
        ui.configure()
        ui.enableDebugCategories(self._cli.get('debug'))
        self._uiInst = ui
