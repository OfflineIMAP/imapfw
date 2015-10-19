#!/usr/bin/python3
#
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

import sys
import traceback

from .conf.main import ImapfwConfig
from .actions.action import Action, Actions
from .toolkit import runHook


class Imapfw(object):
    def run(self):
        config = ImapfwConfig()
        try:
            config.parseCLI() # Parse CLI options.
            config.setupConcurrency() # Exports concurrency to runtime module.
            config.setupUI() # Exports ui to the runtime module.
            ui = config.getUI()
        except Exception as e:
            traceback.print_exc(file=sys.stderr)
            sys.exit(1)

        if config.listActions():
            ui.info("Available actions:")
            for action in sorted(list(Actions.keys())):
                ui.info("- %s: %s"% (action, Action(action).__doc__))
            sys.exit(0)

        try:
            config.loadRascal() # Exports the rascal to the runtime module.
        except FileNotFoundError as e:
            ui.critical(e)
        except Exception:
            raise
            sys.exit(2)


        rascal = config.getRascal()

        # The rascal must use the thread-safe ui, too!
        if rascal is not None:
            rascalConfigure = rascal.getFunction('configure')
            rascalConfigure(ui)

        # "Action", you said? Do you really want action?
        # Fine...
        actionName = config.getAction()
        actionOptions = config.getActionOptions()

        action = Action(actionName)

        if action.requireRascal is True and rascal is None:
            ui.critical("a rascal is required but is not defined, use '-r'.")
            sys.exit(2)

        try:
            if action.honorHooks is True:
                timedout = runHook(rascal.getPreHook(), actionName, actionOptions)
                if timedout:
                    sys.exit(4)

            action.init(actionOptions)
            action.run()
            if action.honorHooks is True:
                timedout = runHook(rascal.getPostHook())
                if timedout:
                    ui.error('postHook reached timed out')
        except Exception as e:
            def outputException(error, message):
                ui.critical(message)
                import traceback, sys
                ui.exception(error)
                traceback.print_exc(file=sys.stdout)

            # Rascal's exceptionHook.
            try:
                if action.honorHooks is True:
                    timedout = runHook(rascal.getExceptionHook(), e)
                    if timedout:
                        ui.error('postHook reached timed out')
            except Exception as hookError:
                outputException(hookError, "exception occured while running"
                    " exceptionHook: %s"% str(hookError))

            # Let the Action instance know the exception.
            try:
                action.exception(e)
            except Exception as actionError:
                outputException(actionError, "exception occured while running"
                    " internal 'action.exception()': %s"% str(actionError))
            raise #TODO: raise only unkown errors.


        sys.exit(action.getExitCode())
