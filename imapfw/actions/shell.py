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
from imapfw.architects import DriverArchitect

from .interface import ActionInterface


class Shell(ActionInterface):
    """Run in (interactive) shell mode."""

    honorHooks = False
    requireRascal = True

    def __init__(self):
        self._repositoryName = None
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
        self._repositoryName = options.get('repository')

    def run(self):
        """Enable the syncing of the accounts in an async fashion.

        Code here is about setting up the environment, start the jobs and
        monitor."""

        import code
        import inspect

        from imapfw.runners.driver import DriverRunner


        class SyncEmitter(object):
            def __init__(self, emitter):
                self.emitter = emitter

            def __getattr__(self, name):
                return getattr(self.emitter, "%s_sync"% name)

        driverArchitect = DriverArchitect("%s.Driver"% self._repositoryName)
        driverArchitect.start()
        driver = driverArchitect.getEmitter()
        d = SyncEmitter(driver)

        d.buildDriverFromRepositoryName(self._repositoryName)

        try:
            from jedi.utils import setup_readline
            setup_readline()
        except ImportError:
            # Fallback to the stdlib readline completer if it is installed.
            # Taken from http://docs.python.org/2/library/rlcompleter.html
            runtime.ui.info("jedi is not installed, falling back to readline"
                " for completion")
            try:
                import readline
                import rlcompleter
                readline.parse_and_bind("tab: complete")
            except ImportError:
                runtime.ui.info("readline is not installed either."
                    " No tab completion is enabled.")


        events = []
        for name, method in inspect.getmembers(
            DriverRunner, inspect.isfunction):
            if name.startswith('_') or name == 'run':
                continue
            events.append("\td.%s%s"% (name, inspect.signature(method)))

        banner = """
Welcome to the shell. The driver is started in a worker. Take control of if with "driver" or "d".
"d" will send any event in sync mode.  Ctrl+D: quit

Available events:
%s
Notice the driver is already built."""% "\n".join(events)

        code.interact(banner=banner, local=locals())

        driverArchitect.stop()
        self._setExitCode(0)
