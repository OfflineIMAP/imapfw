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

from argparse import ArgumentParser

from .. import __version__, __copyright__, __license__
from ..constants import DEBUG_CATEGORIES


class CLIOptions(object):
    """Command line options parser.

    Makes CLI parsing agnostic from the underlying parser."""

    def __init__(self):
        self._options = None

    def parse(self):
        parser = ArgumentParser(
            prog='imapfw',
            description="%s.\n\n%s."% (__copyright__, __license__))

        parser.add_argument("--log-level", dest="info",
            type=int,
            default=3,
            choices=[0, 1, 2, 3],
            help="define the logging level for the output (default is 3)")

        parser.add_argument("-c", dest="concurrency",
            default='multiprocessing',
            choices=['multiprocessing', 'threading'],
            help="the concurrency backend to use (default is multiprocessing)")

        parser.add_argument("-r", dest="rascalfile",
            metavar="RASCAL",
            default=None,
            help="the rascal file to use")

        parser.add_argument("-l", "--list-actions", dest="listActions",
            action='store_true',
            default=False,
            help="list the available actions")

        parser.add_argument("-d", "--debug", dest="debug",
            default=[],
            action='append',
            choices=list(DEBUG_CATEGORIES.keys()),
            help="enable debugging for the requested partial(s)")

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
            )

        # Action: dev
        actions.add_parser('devel',
            help="development")

        # Action: noop
        actions.add_parser('noop',
            help="test if the rascal can be loaded")

        # Action: testRascal
        actions.add_parser('testRascal',
            help="test your rascal")

        # Action: unitTests
        actions.add_parser('unitTests',
            help="run the integrated unit tests")

        # Action: examine
        actions.add_parser('examine',
            help="examine repositories")


        # Action: syncAccounts
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


        # Action: shell
        shell = actions.add_parser('shell',
            help="run in shell mode")
        shell.add_argument("-r", "--repository", dest="repository",
            default=None,
            metavar="REPOSITORY",
            required=True,
            help="a repository")

        #
        # End Actions.
        #

        self._options = vars(parser.parse_args())

    def get(self, name):
        return self._options.get(name)
