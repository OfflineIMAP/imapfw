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


class ShellInterface(object):
    def afterSession(self):     raise NotImplementedError
    def beforeSession(self):    raise NotImplementedError
    def register(self):         raise NotImplementedError
    def session(self):          raise NotImplementedError
    def setBanner(self):        raise NotImplementedError


class Shell(ShellInterface):

    conf = None

    def __init__(self):
        self._env = {}
        self.banner = "Welcome"

    def afterSession(self) -> int:
        return 0

    def configureCompletion(self) -> None:
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

    def beforeSession(self) -> None:
        """Method to set up the environment.

        Set variables required in `run()` as attributes."""
        pass

    def interactive(self) -> None:
        """Run in interactive mode when called."""

        import code
        code.interact(banner=self.banner, local=self._env)

    def register(self, name: str, alias: str=None) -> None:
        """Attribute name to pass to the interpreter.

        The name must be an attribute."""

        if alias is None:
            alias = name
        self._env[alias] = getattr(self, name)

    def session(self) -> None:
        """Run the interactive session by default."""

        self.interactive()

    def setBanner(self, banner: str) -> None:
        """Erase the banner."""

        self.banner = banner


class DriveDriver(Shell):
    """Shell to play with a repository. Actually drive the driver yourself.

    The conf must define the repository to use (str). Start it to learn more.
    """

    conf = {'repository': None}

    def __init__(self):
        super(DriveDriver, self).__init__()

        self.driverArchitect = None
        self.driver = None
        self.d = None

    def afterSession(self):
        self.driverArchitect.stop()
        return 0

    def beforeSession(self):
        import inspect

        from imapfw.runners.driver import DriverRunner
        from imapfw.architects import DriverArchitect
        from imapfw.edmp import SyncEmitter

        repositoryName = self.conf.get('repository')

        self.driverArchitect = DriverArchitect("%s.Driver"% repositoryName)
        self.driverArchitect.start()

        self.driver = self.driverArchitect.getEmitter()
        self.d = SyncEmitter(self.driver)
        self.register('driver')
        self.register('d')

        self.d.buildDriverFromRepositoryName(repositoryName)

        # Setup banner.
        events = []
        for name, method in inspect.getmembers(DriverRunner,
                inspect.isfunction):
            if name.startswith('_') or name == 'run':
                continue
            events.append("\td.%s%s"% (name, inspect.signature(method)))

        banner = """
Welcome to the shell. The driver is started in a worker. Take control of if with "driver" or "d".
"d" will send any event in sync mode.  Ctrl+D: quit

Available events:
%s
Notice the driver is already built with this repository."""% "\n".join(events)
        self.setBanner(banner)
