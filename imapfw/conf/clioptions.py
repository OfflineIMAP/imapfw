# The MIT License (MIT).
# Copyright (c) 2015, Nicolas Sebrecht & contributors.

"""

Parse the command line options.

"""

from argparse import ArgumentParser

from imapfw import __version__, __copyright__, __license__
from imapfw.constants import DEBUG_CATEGORIES

# Annotations.
from imapfw.annotation import ActionClass


class _CLIOptions(object):
    """Command line options parser.

    Makes CLI parsing agnostic from the underlying parser.
    TODO: to be fully agnostic, it must wrap the action sub-parser."""

    def __init__(self):
        self.options = None
        self.parser = None
        self.actions = None
        self.actionClasses = {}

    def addAction(self, name: str, actionClass: ActionClass, help: str):
        self.actionClasses[name] = actionClass
        return self.actions.add_parser(name, help=help)

    def get(self, name):
        return self.options.get(name)

    def getAction(self):
        actionName = self.options.get('action')
        return actionName, self.actionClasses[actionName]

    def init(self):
        self.parser = ArgumentParser(
            prog='imapfw',
            description="%s.\n\n%s."% (__copyright__, __license__))

        self.parser.add_argument("--log-level", dest="info",
            type=int,
            default=3,
            choices=[0, 1, 2, 3],
            help="define the logging level for the output (default is 3)")

        self.parser.add_argument("-c", dest="concurrency",
            default='multiprocessing',
            choices=['multiprocessing', 'threading'],
            help="the concurrency backend to use (default is multiprocessing)")

        self.parser.add_argument("-r", dest="rascalfile",
            metavar="RASCAL",
            default=None,
            help="the rascal file to use")

        self.parser.add_argument("-d", "--debug", dest="debug",
            default=[],
            action='append',
            choices=list(DEBUG_CATEGORIES.keys()),
            help="enable debugging for the requested partial(s)")

        self.parser.add_argument("-v", action='version',
            version=__version__)

        # Actions.
        self.actions = self.parser.add_subparsers(
            title='Available actions',
            prog='action',
            description="Each action might allow its own options. Run"
                " 'imapfw ACTION -h' to know more.",
            metavar='ACTION',
            dest='action',
            )

    def parse(self):
        # Let modules in actions add parsers.
        from imapfw import actions

        self.options = vars(self.parser.parse_args())

Parser = _CLIOptions()
Parser.init()
