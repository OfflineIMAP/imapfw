# The MIT License (MIT).
# Copyright (c) 2015, Nicolas Sebrecht & contributors.

import logging

from imapfw.runtime import set_module
from imapfw.concurrency import Concurrency
from imapfw.rascal import Rascal
from imapfw.ui.tty import TTY

from .clioptions import Parser


class ImapfwConfig(object):
    def __init__(self):
        self.parser = Parser

        self.concurrency = None
        self.rascal = None
        self.ui = None

    def getAction(self):
        return self.parser.getAction()

    def getLogger(self):
        return logging

    def setupConcurrency(self):
        self.concurrency = Concurrency(self.parser.get('concurrency'))
        set_module('concurrency', self.concurrency) # Export concurrency module.

    def loadRascal(self):
        rascalFile = self.parser.get('rascalfile')
        if rascalFile is not None:
            self.rascal = Rascal()
            self.rascal.load(rascalFile)
        set_module('rascal', self.rascal) # Export the rascal.

    def parseCLI(self):
        self.parser.parse()

    def setupUI(self):
        ui = TTY(self.concurrency.createLock())
        ui.configure()

        # Let ui prefix log lines with the worker name.
        ui.setCurrentWorkerNameFunction(self.concurrency.getCurrentWorkerNameFunction())
        # Apply CLI options.
        ui.enableDebugCategories(self.parser.get('debug'))
        ui.setInfoLevel(self.parser.get('info'))

        self.ui = ui
        set_module('ui', ui) # Export ui module.
