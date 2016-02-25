# The MIT License (MIT).
# Copyright (c) 2015, Nicolas Sebrecht & contributors.

import sys
import traceback

from imapfw import runtime
from imapfw.conf import ImapfwConfig, Parser
from imapfw.toolkit import runHook


class Imapfw(object):
    def run(self):
        config = ImapfwConfig()
        try:
            config.parseCLI() # Parse CLI options.
            config.setupConcurrency() # Exports concurrency to runtime module.
            config.setupUI() # Exports ui to the runtime module.
        except Exception as e:
            traceback.print_exc(file=sys.stderr)
            sys.exit(1)

        try:
            config.loadRascal() # Exports the rascal to the runtime module.
        except FileNotFoundError as e:
            runtime.ui.critical(e)
        except Exception:
            raise #FIXME
            sys.exit(2)

        rascal = runtime.rascal
        # The rascal must use the thread-safe ui, too!
        if rascal is not None:
            rascalConfigure = rascal.getFunction('configure')
            rascalConfigure(runtime.ui)

        # "Action", you said? Do you really want action?
        # Fine...
        try:
            actionName, cls_action = config.getAction()
        except KeyError as e:
            runtime.ui.critical("unkown action: %s"% e)
            sys.exit(1)
        action = cls_action()

        if action.requireRascal is True and rascal is None:
            runtime.ui.critical(
                "a rascal is required but is not defined, use '-r'.")
            sys.exit(2)

        try:
            # PreHook.
            if action.honorHooks is True:
                timedout = runHook(rascal.getPreHook(), actionName, Parser)
                if timedout:
                    runtime.ui.critical("preHook reached timeout")
                    sys.exit(4)

            # Doing the job.
            action.init(Parser)
            action.run()

            # PostHook.
            if action.honorHooks is True:
                timedout = runHook(rascal.getPostHook())
                if timedout:
                    runtime.ui.error('postHook reached timed out')
        except Exception as e:
            def outputException(error, message):
                runtime.ui.critical(message)
                import traceback, sys
                runtime.ui.exception(error)
                traceback.print_exc(file=sys.stdout)

            # ExceptionHook.
            try:
                if action.honorHooks is True:
                    timedout = runHook(rascal.getExceptionHook(), e)
                    if timedout:
                        runtime.ui.error('exceptionHook reached timeout')
            except Exception as hookError:
                outputException(hookError, "exception occured while running"
                    " exceptionHook: %s"% str(hookError))

            # Let the Action instance know the exception.
            try:
                # This way, exceptions can be handled in a per-action basis.
                action.exception(e)
            except Exception as actionError:
                outputException(actionError, "exception occured while running"
                    " internal 'action.exception()': %s"% str(actionError))
            raise #TODO: raise only unkown errors.

        sys.exit(action.getExitCode())
