# The MIT License (MIT).
# Copyright (c) 2015, Nicolas Sebrecht & contributors.


from imapfw import runtime
from imapfw.interface import implements, Interface, checkInterfaces


class ShellInterface(Interface):

    scope = Interface.PUBLIC

    def afterSession(self) -> int:
        """What to do on exit. Return the exit code."""

    def beforeSession(self) -> None:
        """Method to set up the environment."""

    def configureCompletion(self) -> None:
        """Configure the complement for theinteractive session."""

    def interactive(self) -> None:
        """Start the interactive session when called."""

    def register(self, name: str, alias: str=None) -> None:
        """Add a variable to the interactive environment.

        Attribute name to pass to the interpreter.  The name MUST be an
        attribute of this object."""

    def session(self) -> None:
        """Build driver and start interactive mode."""

    def setBanner(self, banner: str) -> None:
        """Erase the default banner."""


@checkInterfaces()
@implements(ShellInterface)
class Shell(object):

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
        pass

    def interactive(self) -> None:
        import code
        try:
            code.interact(banner=self.banner, local=self._env)
        except:
            pass

    def register(self, name: str, alias: str=None) -> None:
        if alias is None:
            alias = name
        self._env[alias] = getattr(self, name)

    def session(self) -> None:
        self.interactive()

    def setBanner(self, banner: str) -> None:
        self.banner = banner


class DriveDriverInterface(Interface):
    def buildDriver(self) -> None:
        """Build the driver for the repository in conf."""

@checkInterfaces()
@implements(ShellInterface, DriveDriverInterface)
class DriveDriver(Shell):
    """Shell to play with a repository. Actually drive the driver yourself.

    The conf must define the repository to use (str). Start it to learn more.

    ```
    conf = { 'repository': RepositoryClass }
    ```
    """

    conf = {'repository': None}

    def __init__(self):
        super(DriveDriver, self).__init__()

        self.driverArchitect = None
        self.repository = None
        self.dict_events = None
        self.driver = None
        self.d = None

    def _events(self) -> None:
        print("\n".join(self.dict_events))

    def afterSession(self) -> int:
        self.driverArchitect.stop()
        return 0

    def buildDriver(self) -> None:
        self.d.buildDriverFromRepositoryName(self.repository.getClassName())

    def beforeSession(self) -> None:
        import inspect

        from imapfw.runners.driver import DriverRunner
        from imapfw.types.repository import loadRepository
        from imapfw.architects import DriverArchitect
        from imapfw.edmp import SyncEmitter

        self.repository = loadRepository(self.conf.get('repository'))
        repositoryName = self.repository.getClassName()
        self.driverArchitect = DriverArchitect("%s.Driver"% repositoryName)
        self.driverArchitect.init()
        self.driverArchitect.start()

        self.driver = self.driverArchitect.getEmitter()
        self.d = SyncEmitter(self.driver)
        self.register('driver')
        self.register('d')

        # Setup banner.
        events = []
        for name, method in inspect.getmembers(DriverRunner,
                inspect.isfunction):
            if name.startswith('_') or name == 'run':
                continue
            events.append("- d.%s%s\n%s\n"%
                (name, inspect.signature(method), method.__doc__))
        self.dict_events = events
        self.events = self._events
        self.register('events')

        banner = """
Welcome to the shell! The driver is running in a worker. Take control of it with
the pre-configured emitter. It is available from both the "driver" and
"d" variables.  "d" will send any event in sync mode.  Ctrl+D: quit

Available commands:
- events(): print available events for the driver.

Example:
>>> d.help()

The driver was already built in the default beforeSession() method of this shell.
"""
        self.setBanner(banner)
