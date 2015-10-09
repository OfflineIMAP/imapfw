#!/usr/bin/python3

import sys
import traceback

from .conf.main import ImapfwConfig
from .actions.action import Action, Actions
from .util.toolkit import runHook


class Imapfw(object):
    def run(self):
        config = ImapfwConfig()
        try:
            config.parseCLI() # Parse CLI options.
            config.setupUI()  # Currently, ui is not thread safe!
            ui = config.getUIinst()
        except Exception as e:
            traceback.print_exc(file=sys.stderr)
            sys.exit(1)

        if config.printRascal():
            from .rascal import default
            with open(default.__file__, 'r') as fd:
                print(fd.read())
            sys.exit(0)

        if config.listActions():
            ui.info("Available actions:")
            for action in sorted(list(Actions.keys())):
                ui.info("- %s: %s"% (action, Action(action).__doc__))
            sys.exit(0)

        try:
            config.loadRascal()
        except FileNotFoundError as e:
            ui.critical(e)
        except TypeError:
            ui.critical("no rascal given")
            sys.exit(2)

        actionName = config.getAction()
        actionOptions = config.getActionOptions()

        # Time for the rascal.
        rascal = config.getRascal()
        rascal.configure(ui)

        action = Action(actionName)
        try:
            stop = runHook(rascal.getPreHook(), actionName, actionOptions)
            if stop:
                sys.exit(4)

            action.initialize(ui, rascal, actionOptions)
            action.run()
            runHook(rascal.getPostHook())
        except Exception as e:
            def outputException(error, message):
                ui.critical(message)
                import traceback, sys
                ui.exception(error)
                traceback.print_exc(file=sys.stdout)

            # Rascal's exceptionHook.
            try:
                runHook(rascal.getExceptionHook(), e)
            except Exception as hookError:
                outputException(hookError, "exception occured while running"
                    " exceptionHook: %s"% str(hookError))

            # Let the Action instance know the exception.
            try:
                action.exception(e)
            except Exception as actionError:
                outputException(actionError, "exception occured while running"
                    " internal 'action.exception()': %s"% str(actionError))

            raise

        sys.exit(action.getExitCode())
