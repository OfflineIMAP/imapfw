from argparse import ArgumentParser

from .. import __version__, __copyright__, __license__


class CLIOptions(object):
    """Command line options parser.

    Makes CLI parsing agnostic from the underlying parser."""

    def __init__(self):
        self._options = None

    def parse(self):
        parser = ArgumentParser(
            prog='imapfw',
            description="%s.\n\n%s."% (__copyright__, __license__))

        parser.add_argument("-r", dest="rascalfile",
            metavar="RASCAL",
            help="the rascal file to use")

        parser.add_argument("-R", dest="rascaldefault",
            action='store_true',
            default=False,
            help="print the default rascal file and exit")

        parser.add_argument("-l", "--list-actions", dest="listActions",
            action='store_true',
            default=False,
            help="list the available actions")

        parser.add_argument("-d", "--debug", dest="debug",
            default=[],
            action='append',
            choices=['emitters', 'drivers', 'controllers', 'workers'],
            help="enable debugging for the requested mode(s)")

        #parser.add_argument("--shell", dest="shell",
            #action='store_true',
            #default=False,
            #help="run interactive session to test the rascal file")

        parser.add_argument("-v", action='version',
            version=__version__)

        #
        # Actions.
        #
        actions = parser.add_subparsers(
            title='Available actions',
            prog='action',
            description="Each action might allow its own options. Run"
                " 'imapfw ACTION -h' to know more.",
            metavar='ACTION',
            dest='action',
            #help='choose one of the following actions',
            )

        # noop
        actions.add_parser('noop',
            help="test if the rascal can be loaded")

        # unitTests
        actions.add_parser('unitTests',
            help="run the integrated unit tests")

        # syncAccounts
        syncAccounts = actions.add_parser('syncAccounts',
            help="sync on or more accounts")

        syncAccounts.add_argument("-a", "--account", dest="accounts",
            default=[],
            action='append',
            metavar='ACCOUNT',
            required=True,
            help="one or more accounts to sync")

        syncAccounts.add_argument("-e", "--engine", dest="engine",
            default="SyncAccount",
            help="the sync engine")


        self._options = vars(parser.parse_args())

    def get(self, name):
        return self._options.get(name)
